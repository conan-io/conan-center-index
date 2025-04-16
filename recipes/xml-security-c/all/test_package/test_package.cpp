#include <xercesc/util/PlatformUtils.hpp>
#include <xsec/utils/XSECPlatformUtils.hpp>

int main() {
    xercesc::XMLPlatformUtils::Initialize();
    XSECPlatformUtils::Initialise();
    XSECPlatformUtils::Terminate();
    xercesc::XMLPlatformUtils::Terminate();
    return 0;
}
