cmake_minimum_required(VERSION 3.1)

add_project(aws-sdk-cpp-plugin "C++ AWS SDK plugin" AWS::aws-sdk-cpp-s3)

add_library(${PROJECT_NAME} AwsSdkCppPlugin.cpp)

include(GenerateExportHeader)
generate_export_header(${PROJECT_NAME} BASE_NAME aws_sdk_cpp_plugin)
target_include_directories(${PROJECT_NAME} PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}> $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>)
target_link_libraries(${PROJECT_NAME} PUBLIC ${PROJECT_LIBS})
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 11)

setup_install()

do_packaging()
