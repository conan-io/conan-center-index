cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(oatpp REQUIRED CONFIG)

if ("${oatpp_VERSION}" VERSION_GREATER_EQUAL "1.3.0")
    add_executable(${PROJECT_NAME} test_package.cpp DeserializerTest_1_3_0.cpp)
elseif("${oatpp_VERSION}" VERSION_GREATER_EQUAL "1.1.0")
    add_executable(${PROJECT_NAME} test_package.cpp DeserializerTest_1_1_0.cpp)
else()
    add_executable(${PROJECT_NAME} test_package.cpp DeserializerTest_1_0_0.cpp)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE oatpp::oatpp oatpp::oatpp-test)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
