#include <QCoreApplication>
#include <QObject>
#include <QString>
#include <QTimer>
#include "greeter.h"
#include <QFile>

#include <QNetworkAccessManager>
#include <QtConcurrent>
#include <QDomText>
#include <QSqlDatabase>
#include <QLibraryInfo>
#include <QDir>

#include <qplatformdefs.h>

void f()
{
    qDebug() << "inside f";
}

int main(int argc, char *argv[]){
    QCoreApplication app(argc, argv);
    QCoreApplication::setApplicationName("Application Example");
    QCoreApplication::setApplicationVersion("1.0.0");

    QString name = argc > 0 ? argv[1] : "";
    if (name.isEmpty()) {
        name = "World";
    }

    // check for valid Qt-Plugins folder (see GitHub-Issue #23660; GitHub-PR #24193)
    QString rootPluginFolder = QLibraryInfo::location(QLibraryInfo::PluginsPath);
    QString logMessage;

    if (rootPluginFolder.isEmpty())
    {
        logMessage = "Qt-Plugins folder not found!";
        qCritical() << logMessage;
        return 1;
    }

    QDir dir (rootPluginFolder);
    QFileInfoList list = dir.entryInfoList(QDir::Dirs| QDir::NoSymLinks | QDir::NoDotAndDotDot);

    if (list.isEmpty())
    {
        logMessage = "Qt-Plugins folder is empty!";
        qCritical() << logMessage;
        return 2;
    }

    logMessage = "List of Plugin Modules: ";
    qDebug() << logMessage;
    for (auto &l : list)
    {
        qDebug() << l.baseName();
    }
    // end: check for valid Qt-Plugins folder


    Greeter* greeter = new Greeter(name, &app);
    QObject::connect(greeter, SIGNAL(finished()), &app, SLOT(quit()));
    QTimer::singleShot(0, greeter, SLOT(run()));

    QFile f(":/resource.txt");
    if(!f.open(QIODevice::ReadOnly))
        qFatal("Could not open resource file");
    qDebug() << "Resource content:" << f.readAll();
    f.close();

    qDebug() << W_OK;

    QNetworkAccessManager networkTester;

    QSqlDatabase sqlTester;

    QFuture<void> future = QtConcurrent::run(::f);
    future.waitForFinished();

    QDomText xmlTester;

    return app.exec();
}
