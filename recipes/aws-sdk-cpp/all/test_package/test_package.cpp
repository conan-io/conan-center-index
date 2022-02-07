#include <memory>
#include <aws/core/Aws.h>
#include <AwsSdkCppPlugin.h>


int main() {
    using namespace Aws;
    SDKOptions options;
    InitAPI(options);
    AwsSdkCppPlugin Plugin;
    ShutdownAPI(options);
    return 0;
}

