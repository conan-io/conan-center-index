#include <QApplication>
#include <QUuid>
#include <limereport/LimeReport>
#include <limereport/config.h>
#include <iostream>
#include <QDebug>
#include <QDir>
#include <QFile>
#include <QCommandLineParser>

#ifdef _WIN32
  #include <io.h>
  #include <fcntl.h>
#endif

#include <QStaticPlugin>
#include <QtPlugin>
Q_IMPORT_PLUGIN(QWindowsIntegrationPlugin)

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    QApplication::setApplicationVersion(LIMEREPORT_VERSION_STR);
    QStringList vars;

#if QT_VERSION > QT_VERSION_CHECK(5, 2, 0)
    QCommandLineParser parser;
    parser.addHelpOption();
    parser.addVersionOption();
    QCommandLineOption sourceOption(QStringList() << "s" << "source",
               QCoreApplication::translate("main", "Limereport pattern file name"),
               QCoreApplication::translate("main", "source"));
    parser.addOption(sourceOption);
    QCommandLineOption destinationOption(QStringList() << "d" << "destination",
               QCoreApplication::translate("main", "Output file name"),
               QCoreApplication::translate("main", "destination"));
    parser.addOption(destinationOption);
    QCommandLineOption variablesOption(QStringList() << "p" << "param",
               QCoreApplication::translate("main", "Report parameter (can be more than one)"),
               QCoreApplication::translate("main", "param_name=param_value"));
    parser.addOption(variablesOption);
    parser.process(a);

    LimeReport::ReportEngine report;

    if (parser.value(sourceOption).isEmpty()){
        std::cerr<<"Error! Report file is not specified !! \n";
        return 1;
    }

    if (!report.loadFromFile(parser.value(sourceOption))){
        std::cerr<<"Error! Report file \""+parser.value(sourceOption).toStdString()+"\" not found \n";
        return 1;
    }

    if (!parser.values(variablesOption).isEmpty()){
        foreach(QString var, parser.values(variablesOption)){
            QStringList varItem = var.split("=");
            if (varItem.size() == 2)
                report.dataManager()->setReportVariable(varItem.at(0),varItem.at(1));
        }
    }

    if (parser.value(destinationOption).isEmpty()){
        report.printToPDF(QFileInfo(parser.value(sourceOption)).baseName());
    } else {
        report.printToPDF(parser.value(destinationOption));
    }
#else
    std::cerr<<"This demo intended for Qt 5.2 and higher\n";
#endif
//    QUuid uid = QUuid::createUuid();
//    QString uidStr = uid.toString()+".pdf";
//    report.printToPDF(uidStr);
//    QFile in(uidStr);
//    QFile out;
//    out.open(stdout, QFile::WriteOnly);
//    in.open(QIODevice::ReadOnly);
//#ifdef _WIN32
//    _setmode(fileno(stdout),O_BINARY);
//#endif
//    QByteArray buffer = in.readAll();
//    fwrite(buffer,1,buffer.size(),stdout);
//    in.close();
//    in.remove();

    return 0;
    //return a.exec();
}
