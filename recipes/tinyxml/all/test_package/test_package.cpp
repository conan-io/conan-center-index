#include "tinyxml.h"

int main()
{
    static const char* xml =
        "<?xml version=\"1.0\"?>"
        "<!DOCTYPE PLAY SYSTEM \"play.dtd\">"
        "<PLAY>"
        "<TITLE>A Midsummer Night's Dream</TITLE>"
        "</PLAY>";

    TiXmlDocument doc( "demotest.xml" );
    doc.Parse(xml);

    return 0;
}
