add_project(aws-sdk-cpp-plugin "C++ AWS SDK plugin" AWS::aws-sdk-cpp-s3)

add_library(${PROJECT_NAME} AwsSdkCppPlugin.cpp)

include(GenerateExportHeader)
generate_export_header(${PROJECT_NAME} BASE_NAME aws_sdk_cpp_plugin)
target_include_directories(${PROJECT_NAME} PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}> $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>)
target_link_libraries(${PROJECT_NAME} PUBLIC ${PROJECT_LIBS})
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

setup_install()

do_packaging()
