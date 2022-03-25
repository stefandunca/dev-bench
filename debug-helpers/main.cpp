#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>


int main(int argc, char *argv[])
{
#if QT_VERSION < QT_VERSION_CHECK(6, 0, 0)
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
#endif
    QGuiApplication app(argc, argv);

    QQmlApplicationEngine engine;

    engine.addImportPath("./debug-helpers/");
    engine.addImportPath("./status-desktop/ui/imports");
    engine.addImportPath("./status-desktop/ui/app");
    engine.addImportPath("./status-desktop/ui/StatusQ/src/");
    engine.addImportPath("./debug-helpers/status-desktop/");


    QObject::connect(&engine, &QQmlApplicationEngine::objectCreated, [&engine](QObject *object, const QUrl &url) {
       if(url.toString().endsWith("utils.nim.qml"))
           engine.rootContext()->setContextProperty("globalUtils", object);
    });
    engine.load("./debug-helpers/status-desktop/dummies/utils.nim.qml");

    const QUrl url(QStringLiteral("./debug-helpers/status-desktop/TestStatusDesktop.qml"));
    QObject::connect(&engine, &QQmlApplicationEngine::objectCreated,
                     &app, [url](QObject *obj, const QUrl &objUrl) {
        if (!obj && url == objUrl)
            QCoreApplication::exit(-1);
    }, Qt::QueuedConnection);
    engine.load(url);

    return app.exec();
}
