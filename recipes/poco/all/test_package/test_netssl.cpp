#include "Poco/StreamCopier.h"
#include "Poco/URI.h"
#include "Poco/Exception.h"
#include "Poco/SharedPtr.h"
#include "Poco/Net/SSLManager.h"
#include "Poco/Net/KeyConsoleHandler.h"
#include "Poco/Net/AcceptCertificateHandler.h"
#include "Poco/Net/HTTPSClientSession.h"
#include "Poco/Net/HTTPRequest.h"
#include "Poco/Net/HTTPResponse.h"
#include <memory>
#include <iostream>

using namespace Poco;
using namespace Poco::Net;

class SSLInitializer {
public:
    SSLInitializer() { Poco::Net::initializeSSL(); }

    ~SSLInitializer() { Poco::Net::uninitializeSSL(); }
};

int main(int argc, char** argv) {
    SSLInitializer sslInitializer;

    SharedPtr<InvalidCertificateHandler> ptrCert = new AcceptCertificateHandler(false);
    Context::Ptr ptrContext = new Context(Context::CLIENT_USE, "", Context::VERIFY_NONE);
    SSLManager::instance().initializeClient(0, ptrCert, ptrContext);

    try {
        URI uri("https://httpbin.org/user-agent");
        HTTPSClientSession s(uri.getHost(), uri.getPort());
        HTTPRequest request(HTTPRequest::HTTP_GET, uri.getPath());
        request.set("user-agent", "Poco HTTPSClientSession");
        // FIXME: CCI Jenkins blocks the request making the build fail
        //s.sendRequest(request);
        //HTTPResponse response;
        //std::istream& rs = s.receiveResponse(response);
        //StreamCopier::copyStream(rs, std::cout);
    } catch (const Exception& ex) {
        std::cout << ex.displayText() << std::endl;
        return 1;
    }

    return 0;
}
