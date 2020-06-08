cmake_minimum_required(VERSION 3.16 FATAL_ERROR)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if (HAVE_SSL AND WIN32)
    set(applink_SOURCE ${OPENSSL_INCLUDE_DIR}/openssl/applink.c)
endif()

set (executor_NAME executor)
if (WIN32)
    set (executor_NAME ${executor_NAME}_cpp)
endif()

add_executable(${executor_NAME}
        source/examples/executor/C++/Application.cpp
        source/examples/executor/C++/executor.cpp ${applink_SOURCE})

target_link_libraries(${executor_NAME} ${CONAN_LIBS})

# CTest is a testing tool that can be used to test your project.
# enable_testing()
# add_test(NAME example
#          WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
#          COMMAND example)
