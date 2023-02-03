#include <irrXML.h>

#include <iostream>
#include <string> // we use STL strings to store data in this example
#include <string.h>

int main(int argc, char const* argv[])
{
    if (argc != 2) {
        std::cerr << "usage: " << argv[0] << " <xml_file>" << std::endl;
        return 1;
    }

    irr::io::IrrXMLReader* xml = irr::io::createIrrXMLReader(argv[1]);

    // strings for storing the data we want to get out of the file
    std::string modelFile;
    std::string messageText;
    std::string caption;

    // parse the file until end reached
    while(xml && xml->read())
    {
        switch(xml->getNodeType())
        {
        case irr::io::EXN_TEXT:
            // in this xml file, the only text which occurs is the messageText
            messageText = xml->getNodeData();
            break;
        case irr::io::EXN_ELEMENT:
            {
                if (!strcmp("startUpModel", xml->getNodeName()))
                    modelFile = xml->getAttributeValue("file");
                else
                if (!strcmp("messageText", xml->getNodeName()))
                    caption = xml->getAttributeValue("caption");
            }
            break;
        }
    }

    // delete the xml parser after usage
    delete xml;
    return 0;
}
