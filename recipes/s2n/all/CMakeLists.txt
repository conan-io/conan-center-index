cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper LANGUAGES C)

include(conanbuildinfo.cmake)
conan_basic_setup()

find_package(OpenSSL REQUIRED COMPONENTS Crypto)
add_library(crypto INTERFACE IMPORTED)
set_target_properties(crypto PROPERTIES INTERFACE_LINK_LIBRARIES "OpenSSL::Crypto")

set(SEARCH_LIBCRYPTO OFF)

add_subdirectory(source_subfolder)
