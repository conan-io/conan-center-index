// GraphMain.cpp
#include <xercesc/sax2/SAX2XMLReader.hpp>
#include <xercesc/sax2/XMLReaderFactory.hpp>
#include <xercesc/sax2/ContentHandler.hpp>
#include <xercesc/sax2/DefaultHandler.hpp>
#include <xercesc/sax2/Attributes.hpp>
#include <xercesc/util/PlatformUtils.hpp>
#include <xercesc/framework/LocalFileInputSource.hpp>
#include <stdio.h>
#ifdef WIN32
#include <io.h>
#else
#include <unistd.h>
#endif

#include "GraphHandler.h"
#include "XercesString.h"

#ifdef XERCES_CPP_NAMESPACE_USE
XERCES_CPP_NAMESPACE_USE
#endif

int main(int argc, char* argv[])
{
  if (argc < 2) return -1;

  // initialize the XML library
  XMLPlatformUtils::Initialize();
  // is the file there?
  if ( !access(argv[1], 04) )
  {
    printf("Cheesey Bar Graph!\n");

	XercesString wstrPath(argv[1]);

    SAX2XMLReader* pParser = XMLReaderFactory::createXMLReader();
    LocalFileInputSource source(wstrPath);

	// our application specific handler.
    GraphHandler handler;

    pParser->setFeature( XercesString("http://xml.org/sax/features/validation"), true );
    pParser->setFeature( XercesString("http://apache.org/xml/features/validation/dynamic"), true );
    pParser->setContentHandler(&handler);
    pParser->setErrorHandler(&handler);
    try
    {
      pParser->parse(source);
    }
    catch (...)
    {
      puts("parse error");
    }
  }
  // terminate the XML library
  XMLPlatformUtils::Terminate();
  return 0;
}
