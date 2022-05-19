#include "AwsSdkCppPlugin.h"
#include <aws/core/auth/AWSAuthSigner.h>
#include <aws/core/auth/AWSCredentialsProviderChain.h>
#include <aws/core/client/ClientConfiguration.h>
#include <aws/s3/S3Client.h>

AwsSdkCppPlugin::AwsSdkCppPlugin() {
    using namespace Aws;
    using namespace Auth;
    using namespace Client;
    using namespace S3;
    ClientConfiguration config;
    auto client = MakeShared<S3Client>("S3Client",
            MakeShared<DefaultAWSCredentialsProviderChain>("S3Client"), config,
            AWSAuthV4Signer::PayloadSigningPolicy::Never /*signPayloads*/, true /*useVirtualAddressing*/, US_EAST_1_REGIONAL_ENDPOINT_OPTION::LEGACY);
}
