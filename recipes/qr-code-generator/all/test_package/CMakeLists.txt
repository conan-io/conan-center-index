cmake_minimum_required(VERSION 3.8)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(qr-code-generator REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} qr-code-generator::qr-code-generator)
if (qr-code-generator_VERSION VERSION_LESS "1.7.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE QR_USE_OLD_INCLUDE)
endif()
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
