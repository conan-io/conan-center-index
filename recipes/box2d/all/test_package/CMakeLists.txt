cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if (${BOX2D_VERSION} VERSION_LESS 2.4.0)
    add_executable(${PROJECT_NAME} test_package.cpp)
else()
    add_executable(${PROJECT_NAME} test_package_24.cpp)
endif()
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)