cmake_minimum_required(VERSION 3.15)
project(DS_S3_Uploader)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(AWSSDK REQUIRED)

add_library(ds_s3_uploader STATIC
        src/DSUploader.cpp
)
target_include_directories(ds_s3_uploader PUBLIC include)

target_link_libraries(ds_s3_uploader
        aws-sdk-cpp::aws-sdk-cpp
)


