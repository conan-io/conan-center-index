#include <QGeoView/QGVWidget.h>

#include <QApplication>
#include <QMainWindow>

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    QMainWindow window;

    QGVWidget gvWidget;
    window.setCentralWidget(&gvWidget);

    return 0;
}
