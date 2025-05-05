cmake_minimum_required(VERSION 3.1)

project(test_package CXX)

find_package(qr-code-generator REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE qr-code-generator::qr-code-generator)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

if (qr-code-generator_VERSION VERSION_LESS "1.7.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE QR_USE_OLD_INCLUDE)
endif()
