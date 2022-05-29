cmake_minimum_required(VERSION 3.12)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} main.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 20)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
find_library(M_LIB m)
if(M_LIB)
  target_link_libraries(${PROJECT_NAME} ${M_LIB})
endif()
