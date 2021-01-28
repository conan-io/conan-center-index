#include <iostream>
#include <memory>
#include <aws/core/Aws.h>
#include <aws/core/utils/Outcome.h>
#include <aws/s3/S3Client.h>
#include <aws/s3/model/PutObjectRequest.h>

int main() {
    Aws::SDKOptions options;
    Aws::InitAPI(options);

    Aws::S3::S3Client client;

    auto putObjectRequest = Aws::S3::Model::PutObjectRequest().WithBucket("testbucket").WithKey("testabc/foobar/text.txt");
    auto ss = std::make_shared<std::stringstream>("This is a test");
    putObjectRequest.SetBody(ss);
    auto outcome = client.PutObject(putObjectRequest);

    Aws::ShutdownAPI(options);
    return 0;
}

