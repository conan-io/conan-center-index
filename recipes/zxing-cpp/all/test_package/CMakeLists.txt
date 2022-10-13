cmake_minimum_required(VERSION 3.8)
project(test_package)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(ZXing REQUIRED CONFIG)
find_package(stb REQUIRED CONFIG)

if (ZXing_VERSION VERSION_LESS "1.1.0")
    add_executable(${PROJECT_NAME} test_package.cpp)
else()
    add_executable(${PROJECT_NAME} test_package_1.1.cpp)
endif()
target_link_libraries(${PROJECT_NAME} ZXing::ZXing stb::stb)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
