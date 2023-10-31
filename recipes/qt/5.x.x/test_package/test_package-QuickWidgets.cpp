#include "static_build.h"

#include <QDebug>
#include <QApplication>
#include <QQuickWidget>

int main(int argc, char *argv[]){

    QApplication app{argc, argv};
    QQuickWidget obj;
    qDebug() << obj.initialSize();

    return 0;
}
