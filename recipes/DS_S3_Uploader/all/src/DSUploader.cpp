// DSUploader.cpp
#include "DSUploader.h"
#include <aws/core/Aws.h>
#include <aws/s3/S3Client.h>
#include <aws/s3/model/PutObjectRequest.h>
#include <aws/core/auth/AWSCredentials.h>
#include <fstream>
#include <iostream>

namespace dsu {

    struct DSUploader::Impl {
        Aws::SDKOptions options;
        Aws::S3::S3Client* client;
        Config cfg;

        Impl(const Config & config) : cfg(config) {
            Aws::InitAPI(options);
            Aws::Auth::AWSCredentials credentials(cfg.access_key.c_str(), cfg.secret_key.c_str());

            Aws::Client::ClientConfiguration client_config;
            client_config.scheme = Aws::Http::Scheme::HTTPS;
            client_config.endpointOverride = cfg.endpoint.c_str();
            client_config.region = cfg.region.c_str();
            client_config.verifySSL = cfg.verify_ssl;

            client = new Aws::S3::S3Client(credentials, client_config,
                                           Aws::Client::AWSAuthV4Signer::PayloadSigningPolicy::Never,
                                           false);
        }

        ~Impl() {
            delete client;
            Aws::ShutdownAPI(options);
        }

        bool upload(const std::string& local_path, const std::string& remote_key) {
            Aws::S3::Model::PutObjectRequest object_request;
            object_request.SetBucket(cfg.bucket.c_str());
            object_request.SetKey(remote_key.c_str());

            auto input_data = Aws::MakeShared<Aws::FStream>("PutObjectInputStream",
                                                            local_path.c_str(),
                                                            std::ios_base::in | std::ios_base::binary);

            if (!input_data->good()) {
                std::cerr << "Failed to open file: " << local_path << std::endl;
                return false;
            }

            object_request.SetBody(input_data);

            auto outcome = client->PutObject(object_request);

            if (outcome.IsSuccess()) {
                std::cout << "File uploaded successfully." << std::endl;
                return true;
            } else {
                std::cerr << "Upload failed: " << outcome.GetError().GetMessage() << std::endl;
                return false;
            }
        }
    };

    DSUploader::DSUploader(const Config& config) {
        impl = new Impl(config);
    }

    DSUploader::~DSUploader() {
        delete impl;
    }

    bool DSUploader::upload_file(const std::string& local_path, const std::string& remote_key) {
        return impl->upload(local_path, remote_key);
    }

}
