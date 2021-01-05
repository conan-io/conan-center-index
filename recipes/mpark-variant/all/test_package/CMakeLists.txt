cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(mpark_variant REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} mpark_variant::mpark_variant) # TODO: Remove mpark_variant:: namespace when fixed in conanfile
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
