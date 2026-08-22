cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper LANGUAGES C)

# We want to discover OpenSSL through CMakeDeps and use OpenSSL::Crypto target for linking
# https://github.com/aws/s2n-tls/blob/v1.3.31/CMakeLists.txt#L27-L28
# https://github.com/aws/s2n-tls/blob/v1.3.31/CMakeLists.txt#L379-L381
find_package(OpenSSL REQUIRED)
add_library(crypto INTERFACE IMPORTED)
set_target_properties(crypto PROPERTIES INTERFACE_LINK_LIBRARIES "OpenSSL::Crypto")

add_subdirectory(src)
