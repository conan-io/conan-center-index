cmake_minimum_required(VERSION 3.1)
project(oatpp-libressl-test CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(oatpp-libressl-test oatpp-libressl-test.cpp)
target_link_libraries(oatpp-libressl-test ${CONAN_LIBS} oatpp oatpp-libressl)

# CTest is a testing tool that can be used to test your project.
# enable_testing()
# add_test(NAME oatpp-libressl
#          WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
#          COMMAND oatpp-libressl)
