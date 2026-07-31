#include "Poco/Encodings.h"
#include "Poco/TextEncoding.h"
#include <iostream>


int main() {
    Poco::registerExtraEncodings();
    std::cout << "Poco Encodings: " << Poco::TextEncoding::find("UTF-8")->canonicalName() << std::endl;
    return 0;
}
