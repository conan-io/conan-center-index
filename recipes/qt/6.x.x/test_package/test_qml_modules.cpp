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
    int rc = 0;

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

    QDir dir (rootQMLModules);
    QFileInfoList list = dir.entryInfoList(QDir::Dirs| QDir::NoSymLinks | QDir::NoDotAndDotDot);

    if (list.empty())
    {
        logMessage = "No QML Modules are found!";
        qCritical() << logMessage;
        rc = 1;
    }
    else
    {
        logMessage = "List of QML Modules: ";
        qDebug() << logMessage;
        for (auto &l : list)
        {
            qDebug() << l.baseName();
        }
    }

    a.exit();
    return rc;
}
