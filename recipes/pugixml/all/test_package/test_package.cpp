#include <sstream>
#include <iostream>
#include "pugixml.hpp"

int main() {
    const unsigned majorVersion = PUGIXML_VERSION / 1000;
    const unsigned minorVersion = PUGIXML_VERSION % 1000 / 10;
    const unsigned maintenanceVersion = PUGIXML_VERSION % 1000 % 10;

    std::basic_stringstream<PUGIXML_CHAR> version;
    version << majorVersion << '.' << minorVersion;
    if (maintenanceVersion)
        version << '.' << maintenanceVersion;

    pugi::xml_document doc;
    doc.append_child(PUGIXML_TEXT("PugiXml"))
        .append_attribute(PUGIXML_TEXT("Version"))
        .set_value(version.str().c_str());
    doc.print(std::cout);
}
