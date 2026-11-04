#include <cstdlib>
#include <iostream>
#include <limereport/LimeReport>
#include <limereport/config.h>

int main(int argc, char* argv[])
{
    auto report = new LimeReport::ReportEngine();

    std::cout << "limereport: " << report->reportName().toStdString() << std::endl;
    std::cout << "LIMEREPORT_VERSION_STR: " << LIMEREPORT_VERSION_STR << std::endl;

    delete report;
    return EXIT_SUCCESS;
}
