// DSUploader.h
#pragma once
#include <string>

namespace dsu {

    struct Config {
        std::string access_key;
        std::string secret_key;
        std::string endpoint;
        std::string region = "default";
        std::string bucket;
        bool verify_ssl = true;
    };

    class DSUploader {
    public:
        DSUploader(const Config& config);
        ~DSUploader();

        bool upload_file(const std::string& local_path, const std::string& remote_key);

    private:
        struct Impl;
        Impl* impl;
    };

}
