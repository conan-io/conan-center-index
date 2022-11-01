cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

find_package(psyinf-gmtl REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
# don't link to ${CONAN_LIBS} or CONAN_PKG::package
target_link_libraries(${PROJECT_NAME} PRIVATE psyinf-gmtl::psyinf-gmtl)

