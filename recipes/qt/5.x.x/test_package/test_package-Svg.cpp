#include "static_build.h"

#include <QDebug>
#include <QApplication>
#include <QSvgWidget>

int main(int argc, char *argv[]){

    QApplication app(argc, argv);
    QSvgWidget obj;
    qDebug() << obj.sizeHint();
        
    return 0;
}
