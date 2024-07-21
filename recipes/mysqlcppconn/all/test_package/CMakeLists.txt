cmake_minimum_required(VERSION 3.30)
project(PackageTest CXX)

find_package(mysqlcppconn REQUIRED)
# find_package(OpenSSL REQUIRED)

add_executable(example src/example.cpp)
if(WIN32)
    target_link_libraries(example mysqlcppconn::mysqlcppconn ws2_32 secur32 crypt32 ws2_32 advapi32 user32 bcrypt)
elseif(APPLE)
    target_link_libraries(example mysqlcppconn::mysqlcppconn resolv)
endif()
