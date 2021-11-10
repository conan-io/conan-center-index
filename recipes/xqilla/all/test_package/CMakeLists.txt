cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(XercesC REQUIRED)
find_package(xqilla REQUIRED)

message("xqilla_FOUND: ${xqilla_FOUND}")
message("xqilla_INCLUDE_DIR: ${xqilla_INCLUDE_DIR}")
message("xqilla_LIBS: ${xqilla_LIBS}")
message("xqilla_LIBRARIES: ${xqilla_LIBRARIES}")
message("xqilla_VERSION: ${xqilla_VERSION}")

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} XercesC::XercesC xqilla::xqilla)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
