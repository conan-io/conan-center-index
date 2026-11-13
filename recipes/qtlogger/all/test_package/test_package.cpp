#include <QCoreApplication>

#include <qtlogger/qtlogger.h>

int main(int argc, char *argv[])
{
    QCoreApplication app(argc, argv);

    gQtLogger.configure();
    
    qInfo("qtlogger test package");

    return 0;
}
