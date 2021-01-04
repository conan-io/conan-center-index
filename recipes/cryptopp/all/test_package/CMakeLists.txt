cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(cryptopp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
# TODO: remove cryptopp:: namespace when fixed in conanfile.py of cryptopp
if(CRYPTOPP_SHARED)
  target_link_libraries(${PROJECT_NAME} cryptopp::cryptopp-shared)
else()
  target_link_libraries(${PROJECT_NAME} cryptopp::cryptopp-static)
endif()
