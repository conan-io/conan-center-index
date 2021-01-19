cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
conan_target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
