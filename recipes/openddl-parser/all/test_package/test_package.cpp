#include <openddlparser/OpenDDLExport.h>
#include <openddlparser/OpenDDLParser.h>
#include <iostream>

USE_ODDLPARSER_NS

int main()
{
    OpenDDLParser oddlParser;
    const bool result(oddlParser.parse());
    OpenDDLExport oddlExporter;
    return EXIT_SUCCESS;
}
