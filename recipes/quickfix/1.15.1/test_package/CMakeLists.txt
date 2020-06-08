cmake_minimum_required(VERSION 3.16 FATAL_ERROR)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set (executor_NAME executor)
if (WIN32)
    set (executor_NAME ${executor_NAME}_cpp)
endif()

add_executable(${executor_NAME}
        ${PROJECT_SOURCE_DIR}/source/examples/executor/C++/Application.cpp
        ${PROJECT_SOURCE_DIR}/source/examples/executor/C++/executor.cpp)

target_link_libraries(${executor_NAME} ${CONAN_LIBS})

# CTest is a testing tool that can be used to test your project.
# enable_testing()
# add_test(NAME example
#          WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
#          COMMAND example)
