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
    QFile file("test_qml_module_output.txt");
    if (file.open(QIODevice::Text | QIODevice::ReadWrite))
    {
        QTextStream stream(&file);
        for (auto &modulePath: modulePaths)
        {
            if (QDir(modulePath).exists())
            {
                if (QDir(modulePath).dirName() == "qml")
                {
                    logMessage = "QML Module Directory: ";
                    qDebug() <<  logMessage << modulePath;
                    stream << logMessage << modulePath << "\n";

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
            qDebug() << logMessage;
            stream << logMessage  << "\n";
        }
        else
        {
            logMessage = "List of QML Modules: ";
            qDebug() << logMessage;
            stream << logMessage << "\n";
            for (auto &l : list)
            {
                qDebug() << l.baseName();
                stream << l.baseName() << "\n";
            }
        }
    }

    file.close();


    return a.exec();
}
