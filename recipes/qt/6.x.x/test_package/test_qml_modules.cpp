#include <QCoreApplication>
#include <QQmlEngine>
#include <QFileInfo>
#include <QDir>
#include <QFileInfoList>
#include <QDebug>
#include <QTextStream>

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);

    QQmlEngine engine;
    QStringList modulePaths = engine.importPathList();
    QString rootQMLModules;
    QString logMessage;

    for (auto &modulePath: modulePaths)
    {
        if (QDir(modulePath).exists())
        {
            if (QDir(modulePath).dirName() == "qml")
            {
                logMessage = "QML Module Directory: ";
                qDebug() <<  logMessage << modulePath;

                rootQMLModules = modulePath;
                break;
            }
        }
    }

    // QCoreApplication is only needed while we look up the path from the QQmlEngine
    a.exit();

    if (rootQMLModules.isEmpty())
    {
        logMessage = "No QML Modules are found!";
        qCritical() << logMessage;
        return 1;
    }

    QDir dir (rootQMLModules);
    QFileInfoList list = dir.entryInfoList(QDir::Dirs| QDir::NoSymLinks | QDir::NoDotAndDotDot);

    logMessage = "List of QML Modules: ";
    qDebug() << logMessage;
    for (auto &l : list)
    {
        qDebug() << l.baseName();
    }

    return 0;
}
