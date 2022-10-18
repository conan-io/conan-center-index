#include <QApplication>
#include <QQmlApplicationEngine>

#include <runtimeqml.hpp>

int main(int argc, char* argv[]) {
    QApplication app(argc, argv);
    QQmlApplicationEngine engine;

    RuntimeQml* rt = new RuntimeQml(&engine);
    return app.exec();
}
