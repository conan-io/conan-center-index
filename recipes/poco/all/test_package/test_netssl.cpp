#include "Poco/Net/Context.h"
#include "Poco/Net/HTTPSClientSession.h"
#include "Poco/Net/SSLManager.h"
#include "Poco/URI.h"

using namespace Poco::Net;
using Poco::Net::Context;
using Poco::Net::HTTPSClientSession;
using Poco::URI;

class SSLInitializer {
public:
   SSLInitializer() { Poco::Net::initializeSSL(); }

   ~SSLInitializer() { Poco::Net::uninitializeSSL(); }
};

int main()
{
   SSLInitializer sslInitializer;
   URI uri("https://pocoproject.org/");
   return 0;
}
