#include <iostream>
#include <memory>
#include <aws/core/Aws.h>
#include <aws/core/auth/AWSAuthSigner.h>
#include <aws/core/auth/AWSCredentialsProviderChain.h>
#include <aws/core/client/ClientConfiguration.h>
#include <aws/s3/S3Client.h>


int main() {
    using namespace Aws;
    using namespace Auth;
    using namespace Client;
    using namespace S3;
    SDKOptions options;
    InitAPI(options);
    ClientConfiguration config;
    auto client = MakeShared<S3Client>("S3Client",
            MakeShared<DefaultAWSCredentialsProviderChain>("S3Client"), config,
            AWSAuthV4Signer::PayloadSigningPolicy::Never /*signPayloads*/, true /*useVirtualAddressing*/, US_EAST_1_REGIONAL_ENDPOINT_OPTION::LEGACY);
    ShutdownAPI(options);
    return 0;
}

