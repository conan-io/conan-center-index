cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(ValiJSON REQUIRED CONFIG)
find_package(nlohmann_json REQUIRED CONFIG)
find_package(picojson REQUIRED CONFIG)
find_package(RapidJSON REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
target_link_libraries(
    ${PROJECT_NAME}
    ValiJSON::valijson
    nlohmann_json::nlohmann_json
    picojson::picojson
    RapidJSON::RapidJSON
)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
