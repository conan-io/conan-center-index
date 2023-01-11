#include <limereport/LimeReport>
#include <limereport/config.h>

#include <QCoreApplication>
#include <iostream>


int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);

    LimeReport::ReportEngine report;
    std::cout << LIMEREPORT_VERSION_STR << std::endl;

    return 0;
}
