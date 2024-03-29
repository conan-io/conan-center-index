cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(OpenSSL REQUIRED)
find_package(CURL REQUIRED)
find_package(INSPURCLOUD_OSS_CPP_SDK REQUIRED)
add_executable(${PROJECT_NAME} example_basic.cc)
target_include_directories(${PROJECT_NAME} PRIVATE
        ${OpenSSL_INCLUDE_DIRS}
        ${CURL_INCLUDE_DIRS}
        ${INSPURCLOUD_OSS_CPP_SDK_INCLUDE_DIRS}
)
target_link_libraries(${PROJECT_NAME} PRIVATE
        ${OpenSSL_LIBRARIES}
        ${CURL_LIBRARIES}
        ${INSPURCLOUD_OSS_CPP_SDK_LIBRARIES}
)
