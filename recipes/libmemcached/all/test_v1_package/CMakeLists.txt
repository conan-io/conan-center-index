cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

find_package(libmemcached REQUIRED)

add_executable(${PROJECT_NAME} src/example.cpp)
#target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
target_link_libraries(${PROJECT_NAME} libmemcached::libmemcached)
