cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(jinja2cpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} jinja2cpp::jinja2cpp) # TODO: remove jinja2cpp:: when fixed in cpp_info of conanfile.py
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 14)
