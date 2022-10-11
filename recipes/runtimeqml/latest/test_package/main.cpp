#include <QApplication>
#include <QQmlApplicationEngine>

#include <runtimeqml.hpp>

int main(int argc, char* argv[]) {
    QApplication app(argc, argv);
    QQmlApplicationEngine engine;

    RuntimeQml* rt = new RuntimeQml(&engine);
    rt->parseQrc(ROOT_SOURCE_PATH "/qml.qrc");
    rt->setAutoReload(true); // Reload automatically on file update
    rt->load(QStringLiteral("qrc:/main.qml"));
    return app.exec();
}
