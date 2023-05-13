#include <QCoreApplication>
#include <QGuiApplication>
#include <iostream>
#include <limereport/LimeReport>
#include <limereport/config.h>

int main(int argc, char* argv[])
{
    QGuiApplication a(argc, argv);

    if ((!QCoreApplication::instance())) {
        qFatal("QPrinter: Must construct a QCoreApplication before a QPrinter");
    } else {
        qInfo("CoreApplication exists");
    }

    auto report = new LimeReport::ReportEngine();

    std::cout << report->reportName().toStdString() << std::endl;
    std::cout << LIMEREPORT_VERSION_STR << std::endl;

    delete report;
    return a.exec();
}
