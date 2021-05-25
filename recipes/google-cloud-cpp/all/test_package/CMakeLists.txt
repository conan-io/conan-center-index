cmake_minimum_required(VERSION 3.5)
project(google-cloud-cpp-storage-quickstart CXX C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(google-cloud-cpp REQUIRED)

# Once the packages are found, define the targets.
add_executable(storage storage.cpp)
target_link_libraries(storage google-cloud-cpp::storage)
