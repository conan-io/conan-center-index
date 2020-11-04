cmake_minimum_required(VERSION 3.1)
project(oatpp-postgresql-test CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(oatpp-postgresql-test oatpp-postgresql-test.cpp)
target_link_libraries(oatpp-postgresql-test ${CONAN_LIBS} oatpp pq)

# CTest is a testing tool that can be used to test your project.
# enable_testing()
# add_test(NAME oatpp-postgresql
#          WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
#          COMMAND oatpp-postgresql)
