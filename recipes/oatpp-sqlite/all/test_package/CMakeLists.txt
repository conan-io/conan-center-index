cmake_minimum_required(VERSION 3.1)
project(oatpp-sqlite-test CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(oatpp-sqlite-test oatpp-sqlite-test.cpp)
target_link_libraries(oatpp-sqlite-test ${CONAN_LIBS} oatpp)

# CTest is a testing tool that can be used to test your project.
# enable_testing()
# add_test(NAME oatpp-sqlite
#          WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
#          COMMAND oatpp-sqlite)
