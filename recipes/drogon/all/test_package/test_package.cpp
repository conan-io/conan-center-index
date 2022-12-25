#include "drogon/drogon.h"

int main() {
    trantor::Logger::setLogLevel(trantor::Logger::kTrace);

    auto client = drogon::HttpClient::newHttpClient("http://www.example.com");
    auto req    = drogon::HttpRequest::newHttpRequest();
    req->setMethod(drogon::Get);
    req->setPath("/s");
    req->setParameter("wd", "wx");
    req->setParameter("oq", "wx");

    return 0;
}
