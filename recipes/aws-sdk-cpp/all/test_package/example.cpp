#include <iostream>
#include <memory>
#include <aws/core/Aws.h>


int main() {
    using namespace Aws;
    SDKOptions options;
    InitAPI(options);
    ShutdownAPI(options);
    return 0;
}

