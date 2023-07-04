#include "static_build.h"

#include <QDebug>
#include <QGuiApplication>

int main(int argc, char *argv[])
{
    QGuiApplication app{argc, argv};
    qDebug() << app.platformName();
    
    return 0;
}
