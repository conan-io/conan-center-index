#include <QApplication>
#include <limereport/LimeReport>
#include <limereport/config.h>
#include <iostream>


int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

    LimeReport::ReportEngine report;
    std::cout<< LIMEREPORT_VERSION_STR << std::endl;

    return 0;
}
