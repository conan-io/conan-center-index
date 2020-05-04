/*
 * Copyright 2017 Sony Corporation
 */

#include "easyhttpcpp/EasyHttp.h"

#include <iostream>
#include <stdexcept>

void displayUsage(char** argv)
{
    std::cout << "Usage: " << argv[0] << " <url>" << std::endl;
    std::cout << "       Fetches the resource identified by <url> and prints it to the standard output"
              << std::endl;
}

void dumpResponse(easyhttpcpp::Response::Ptr pResponse)
{
    std::cout << "Http status code: " << pResponse->getCode() << std::endl;
    std::cout << "Http status message: " << pResponse->getMessage() << std::endl;
    std::cout << "Http response headers:\n" << pResponse->getHeaders()->toString() << std::endl;

    // dump response body if text
    const std::string contentType = pResponse->getHeaderValue("Content-Type", "");
    if (Poco::isubstr<std::string>(contentType, "text/html") != std::string::npos) {
        std::cout << "Http response body:\n" << pResponse->getBody()->toString() << std::endl;
    }
}

int main(int argc, char** argv)
{
    // need a url to execute easyhttpcpp http client
    if (argc < 2) {
        displayUsage(argv);
        return 1;
    }
    std::string url = argv[1];

    // HTTP GET the url
    std::cout << "HTTP GET url: " << url << std::endl;

    try {
        // cache dir = current working dir; cache size = 100 KB
        easyhttpcpp::HttpCache::Ptr pCache = easyhttpcpp::HttpCache::createCache(Poco::Path::current(), 1024 * 100);

        // a default http connection pool
        easyhttpcpp::ConnectionPool::Ptr pConnectionPool = easyhttpcpp::ConnectionPool::createConnectionPool();

        // configure http cache and connection pool instance (optional but recommended)
        easyhttpcpp::EasyHttp::Builder httpClientBuilder;
        httpClientBuilder.setCache(pCache)
                .setConnectionPool(pConnectionPool);

        // create http client
        easyhttpcpp::EasyHttp::Ptr pHttpClient = httpClientBuilder.build();

        // create a new request and execute synchronously
        easyhttpcpp::Request::Builder requestBuilder;
        easyhttpcpp::Request::Ptr pRequest = requestBuilder.setUrl(url).build();
        easyhttpcpp::Call::Ptr pCall = pHttpClient->newCall(pRequest);
        easyhttpcpp::Response::Ptr pResponse = pCall->execute();

        if (!pResponse->isSuccessful()) {
            std::cout << "HTTP GET Error: (" << pResponse->getCode() << ")" << std::endl;
        } else {
            std::cout << "HTTP GET Success!" << std::endl;
        }

        // dump response
        dumpResponse(pResponse);
    } catch (const std::exception& e) {
        std::cout << "Error occurred: " << e.what() << std::endl;
    }

    return 0;
}
