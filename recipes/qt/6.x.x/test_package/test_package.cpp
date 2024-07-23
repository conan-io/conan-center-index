#include <QCoreApplication>
#include <QObject>
#include <QString>
#include <QTimer>
#include <QFile>

#include <QNetworkAccessManager>
#include <QSqlDatabase>
#include <qtconcurrentfilter.h>
#include <QDomText>
#include <QLibraryInfo>
#include <QDir>

#include "greeter.h"

int main(int argc, char *argv[]){
    QCoreApplication app(argc, argv);
    QCoreApplication::setApplicationName("Application Example");
    QCoreApplication::setApplicationVersion("1.0.0");

    QString name = argc > 0 ? argv[1] : "";
    if (name.isEmpty()) {
        name = "World";
    }

    Greeter* greeter = new Greeter(name, &app);
    QObject::connect(greeter, SIGNAL(finished()), &app, SLOT(quit()));
    QTimer::singleShot(0, greeter, SLOT(run()));

    QFile f(":/resource.txt");
    if(!f.open(QIODevice::ReadOnly))
        qFatal("Could not open resource file");
    qDebug() << "Resource content:" << f.readAll();
    f.close();

    QNetworkAccessManager networkTester;

    QSqlDatabase sqlTester;

    QVector<int> v;
    v << 1 << 2 << 3 << 4;
    QtConcurrent::blockingFilter(v, [](int i)
    {
        return i % 2;
    });

    QDomText xmlTester;


    QString rootPluginFolder = QLibraryInfo::path(QLibraryInfo::PluginsPath);
    QString logMessage;

    if (rootPluginFolder.isEmpty())
    {
        logMessage = "No Pplugins are found!";
        qCritical() << logMessage;
        return 1;
    }

    QDir dir (rootPluginFolder);
    QFileInfoList list = dir.entryInfoList(QDir::Dirs| QDir::NoSymLinks | QDir::NoDotAndDotDot);

    logMessage = "List of Plugin Modules: ";
    qDebug() << logMessage;
    for (auto &l : list)
    {
        qDebug() << l.baseName();
    }

    return app.exec();
}
