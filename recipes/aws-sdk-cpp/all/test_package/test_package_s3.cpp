// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0

#include <iostream>
#include <aws/core/Aws.h>
#include <aws/s3/S3Client.h>
#include <aws/s3/model/ListObjectsV2Request.h>
#include <aws/s3/model/Object.h>

bool listObjects(const Aws::S3::S3ClientConfiguration &clientConfig) {
    Aws::S3::S3Client s3Client(clientConfig);

    return true;
}

int main(int argc, char* argv[])
{

    Aws::SDKOptions options;
    Aws::InitAPI(options);
    {
        const Aws::String bucketName = "";

        Aws::S3::S3ClientConfiguration clientConfig;
        listObjects(clientConfig);
    }
    Aws::ShutdownAPI(options);

    return 0;
}

