cmake_minimum_required(VERSION 3.8)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(bitserializer REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME}
    BitSerializer::core
    $<$<BOOL:${WITH_CPPRESTSDK}>:BitSerializer::cpprestjson-archive>
    $<$<BOOL:${WITH_RAPIDJSON}>:BitSerializer::rapidjson-archive>
    $<$<BOOL:${WITH_PUGIXML}>:BitSerializer::pugixml-archive>)
target_compile_definitions(${PROJECT_NAME} PRIVATE
    $<$<BOOL:${WITH_CPPRESTSDK}>:"WITH_CPPRESTSDK">
    $<$<BOOL:${WITH_RAPIDJSON}>:"WITH_RAPIDJSON">
    $<$<BOOL:${WITH_PUGIXML}>:"WITH_PUGIXML">)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
