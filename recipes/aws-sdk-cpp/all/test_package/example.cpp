#include <iostream>
#include <memory>
#include <aws/core/Aws.h>
#include <aws/core/utils/logging/AWSLogging.h>
#include <aws/core/utils/logging/DefaultLogSystem.h>


int main() {
    using namespace Aws;
    SDKOptions options;
    Utils::Logging::InitializeAWSLogging(
            MakeShared<Utils::Logging::DefaultLogSystem>(
                "LogSystem", Utils::Logging::LogLevel::Trace, "aws_sdk_"));
    InitAPI(options);
    ShutdownAPI(options);
    return 0;
}

