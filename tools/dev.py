#!/usr/bin/env python3
import sh
import click
import glob
import json
import os
from dataclasses import dataclass

script_dir = os.path.dirname(os.path.abspath(__file__))
config_file = f"{script_dir}/.dev_config.json"

@dataclass
class Config:
    project_path: script_dir

@dataclass
class CtxObject:
    config: Config

def save_config(config: Config):
    json.dump(config.__dict__, open(config_file, 'w'), indent=2)

@click.group()
@click.pass_context
def cli(ctx):
    # Setup context object
    obj = CtxObject
    if os.path.exists(config_file):
        obj.config = Config(**json.load(open(config_file)))
    else:
        obj.config = Config(project_path=os.path.expanduser(f"{script_dir}/../status-desktop"))
        save_config(obj.config)

    ctx.obj = obj

    # No command, run default
    if ctx.invoked_subcommand is None:
        # TODO: update packages
        pass

std_out = {'_out': click.get_text_stream('stdout'), '_err_to_out':True}

def get_out(log_file_path):
    def custom_tee(line):
        with open(log_file_path, 'a') as f:
            f.write(line)
        print(line.strip())
    return {"_out": custom_tee, "_err_to_out":True,}

@cli.command(help="Run wallet tests")
@click.option('--activity', '-u', is_flag=True, help="Update docker image")
@click.option('--log_file', '-l', default='~/proj/status/tmp/status-go-tests.log', help="Out log file path")
@click.option('--append/--no-append', default=False, help="Clear log file")
@click.option('--track', '-t', is_flag=True, help="Use nodemon to track file changes and rerun tests")
@click.option('--ext' , default='*.go,*.sql', help="File extensions to track")
@click.pass_obj
def test(obj: CtxObject, activity, log_file, append, track, ext):
    test_dirs = []
    if activity:
        test_dirs = ['./services/wallet/activity/...']
    else:
        test_dirs = [   './services/wallet/...',
                        './transactions/...',
                        './appdatabase/...',
                        './walletdatabase/...',
                    ]

    log_file = os.path.expanduser(log_file)

    # Clear log file first
    if not append:
        with open(log_file, 'w') as f:
            pass

    cmd = sh.go.test.bake('-v',
        *test_dirs, **get_out(log_file), tags="gowaku_skip_migrations",
        _cwd=os.path.join(obj.config.project_path, 'vendor/status-go'))


    if track:
        cmd_str = str(cmd) + f" 2>&1 | tee {log_file} || exit 1"
        sh.nodemon('--ext', ext, "--exec", cmd_str, **std_out)
    else:
        cmd()

import re
import time
from tabulate import tabulate

@cli.command(help="Run activity benchmarks")
@click.option('--bench', '-b', default='BenchmarkGetActivityEntries', help="Benchmark to run")
@click.option('--record', '-e', default=None, help="Benchmark to save results to")
@click.option('--summary', '-o', default=None, help="Summary output Markdown file")
@click.pass_obj
def benchmark(obj: CtxObject, bench, record, summary):
    extras = []
    out = std_out

    history = {}
    current_res = []
    timestamp = int(time.time())
    res_file = f"{script_dir}/../debugging/benchmarks.json"
    if record and os.path.exists(res_file):
        with open(res_file, 'r') as f:
            history = json.load(f)

    if record:
        extras = ['-json']
        def parse_perf(line):
            data = json.loads(line)
            if "Output" in data:
                match = re.search(r'^(.+?)\s+\d+\s+(\d+)\s+ns/op', data["Output"])
                if match:
                    name = match.group(1)
                    ns = int(match.group(2))
                    print(f"{name}: {ns} ns/op")
                    current_res.append({"bench": name, "ns": ns})

        out = {'_out': parse_perf, '_err': click.get_text_stream('stderr')}

    sh.go.test('-v', "./services/wallet/activity/...", benchtime='10x', run='^$', bench=bench, *extras,
        tags="gowaku_skip_migrations", **out,
        _cwd=os.path.join(obj.config.project_path, 'vendor/status-go'))

    if record:
        history[record] = {"timestamp": timestamp, "results": current_res}
        with open(res_file, 'w') as f:
            json.dump(history, f, indent=2)

    if summary:
        with open(os.path.expanduser(summary), 'w') as f:
            f.write(f"# Activity filter optimizations\n\n")

            headers = [k for k, _ in sorted(history.items(), key=lambda x: x[1]['timestamp'])]

            benchmarks = {}
            for header in headers:
                for res in history[header]["results"]:
                    name = res["bench"]
                    if name not in benchmarks:
                        benchmarks[name] = [name.split("/")[-1]]
                    benchmarks[name].append(res["ns"])

            headers = ["Name", *headers]
            data = [headers, *benchmarks.values()]
            markdown_table = tabulate(data, headers="firstrow", tablefmt="pipe")
            f.write(markdown_table)
            f.write("\n")


def echo(message):
    click.echo(f'DEV: {message}')

if __name__ == '__main__':
    try:
        cli()
    except sh.ErrorReturnCode as e:
        echo(f'Command "{e.full_cmd}" failed with exit code {e.exit_code}')