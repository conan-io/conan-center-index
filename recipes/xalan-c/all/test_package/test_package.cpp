#include <xalanc/XalanTransformer/XalanTransformer.hpp>

int main(int argc, char* argv[])
{
  try {
    xercesc::XMLPlatformUtils::Initialize();
  }
  catch (const xercesc::XMLException& toCatch) {
    return 1;
  }

  xalanc::XalanTransformer::initialize();

  {
      xalanc::XalanTransformer xalan;
      xalan.setStylesheetParam("param1", "'What is Up'");
  }

  xalanc::XalanTransformer::terminate();

  xercesc::XMLPlatformUtils::Terminate();

  return 0;
}
