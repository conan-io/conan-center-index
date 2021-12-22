cmake_minimum_required(VERSION 3.7)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(oatpp REQUIRED CONFIG)

if ("${oatpp_VERSION}" VERSION_GREATER_EQUAL "1.3.0")
    add_executable(${PROJECT_NAME} example.cpp DeserializerTest_1_3_0.cpp)
elseif("${oatpp_VERSION}" VERSION_GREATER_EQUAL "1.1.0")
    add_executable(${PROJECT_NAME} example.cpp DeserializerTest_1_1_0.cpp)
else()
    add_executable(${PROJECT_NAME} example.cpp DeserializerTest_1_0_0.cpp)
endif()
target_link_libraries(${PROJECT_NAME} oatpp::oatpp oatpp::oatpp-test)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
