#include "static_build.h"

#include <QDebug>
#include <QApplication>
#include <QChart>

int main(int argc, char *argv[]){

    QApplication app(argc, argv);
    QtCharts::QChart obj;
    qDebug() << obj.title();

    return 0;
}
