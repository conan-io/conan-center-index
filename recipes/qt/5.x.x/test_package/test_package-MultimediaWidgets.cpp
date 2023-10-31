#include "static_build.h"

#include <QDebug>
#include <QApplication>
#include <QVideoWidget>

int main(int argc, char *argv[]){

    QApplication app{argc, argv};
    QVideoWidget videoWidget;
    qDebug() << videoWidget.isFullScreen();
        
    return 0;
}
