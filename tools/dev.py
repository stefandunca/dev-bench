#!/usr/bin/env python3
import sh
import click
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
@click.option('--project_path', '-p', default=None, help="Override project path in config")
def cli(ctx, project_path):
    # Setup context object
    obj = CtxObject
    if os.path.exists(config_file):
        obj.config = Config(**json.load(open(config_file)))
    else:
        obj.config = Config(project_path=os.path.expanduser(f"{script_dir}/../status-desktop"))
        save_config(obj.config)

    if project_path is not None:
        obj.config.project_path = os.path.abspath(os.path.expanduser(project_path))
        echo(f"Project path overwritten to {obj.config.project_path}")

    ctx.obj = obj

    echo(f"Project path: {obj.config.project_path}")

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

status_go_tags="gowaku_no_rln,gowaku_skip_migrations"

@cli.command(help="Run wallet tests or any tests in 'test_dir'")
@click.option('--test_dir', '-d', help="Test directory to run e.g. --test_dir './services/wallet/activity/...'")
@click.option('--log_file', '-l', default='~/proj/status/tmp/status-go-tests.log', help="Out log file path")
@click.option('--append/--no-append', default=False, help="Clear log file")
@click.option('--track', '-t', is_flag=True, help="Use nodemon to track file changes and rerun tests")
@click.option('--watch', '-w', is_flag=True, help="Run test in a loop until it fails")
@click.option('--ext' , default='*.go,*.sql', help="File extensions to track")
@click.option('--run', '-r', default=None, help="Run tests matching")
@click.option('--no-cache', is_flag=True, help="Disable test caching")
@click.pass_obj
def test(obj: CtxObject, test_dir, log_file, append, track, ext, run, watch, no_cache):
    if watch and track:
        raise Exception("Cannot use --watch and --track at the same time")

    test_dirs = []
    if test_dir:
        test_dirs = [test_dir]
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

    run_opt = []
    if run:
        run_opt = ['-run', run]

    if no_cache:
        run_opt.append('-count=1')

    proj_path = os.path.join(obj.config.project_path, 'vendor/status-go')
    cmd = sh.go.test.bake('-v',
        *test_dirs, *run_opt, **get_out(log_file), tags=status_go_tags,
        _cwd=proj_path)


    cmd_str = str(cmd) + f" 2>&1 | tee {log_file}"
    exec_count = 0
    if track:
        sh.nodemon('--ext', ext, "--exec", cmd_str, **std_out, _cwd=proj_path)
    elif watch:
        while True:
            exec_count += 1
            echo(f"Iteration [{exec_count}]\n")
            cmd(**std_out)
    else:
        cmd(**std_out)

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
        tags=status_go_tags, **out,
        _cwd=os.path.join(obj.config.project_path, 'vendor/status-go'))

    if record:
        history[record] = {"timestamp": timestamp, "results": current_res}
        with open(res_file, 'w') as f:
            json.dump(history, f, indent=2)

    if summary:
        with open(os.path.expanduser(summary), 'w') as f:
            f.write(f"# Activity filter optimizations\n\n")

            columns = [k for k, _ in sorted(history.items(), key=lambda x: x[1]['timestamp'])]
            benchmarks = {}
            for column in columns:
                for res in history[column]["results"]:
                    name = res["bench"]
                    if name not in benchmarks:
                        benchmarks[name] = [name.split("/")[-1]]

            for column in columns:
                for bench in benchmarks.keys():
                    entry = '-'
                    for res in history[column]["results"]:
                        name = res["bench"]
                        if name == bench:
                            entry = res["ns"]
                            break
                    benchmarks[bench].append(entry)

            columns = ["Name", *columns]
            data = [columns, *benchmarks.values()]
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