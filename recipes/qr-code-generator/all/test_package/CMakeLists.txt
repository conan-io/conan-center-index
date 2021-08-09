cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
if (QRCODEGEN_VERSION VERSION_LESS "1.7.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE QR_USE_OLD_INCLUDE)
endif()

set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
