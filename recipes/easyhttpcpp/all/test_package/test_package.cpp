#include <easyhttpcpp/common/ProjectVersion.h>
#include <iostream>


int main() {
    std::cout << "EasyHttpCpp version: " << easyhttpcpp::common::ProjectVersion::asString() << "\n";
    return 0;
}
