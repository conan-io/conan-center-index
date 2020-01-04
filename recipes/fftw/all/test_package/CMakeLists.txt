project(test_package)
cmake_minimum_required(VERSION 2.8.11)

option(ENABLE_SINGLE_PRECISION "Enable FFTW single precision" OFF)
option(ENABLE_LONG_DOUBLE_PRECISION "Enable FFTW single precision" OFF)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

target_compile_options(${PROJECT_NAME} PRIVATE
    $<$<BOOL:${ENABLE_SINGLE_PRECISION}>:-DENABLE_SINGLE_PRECISION=1>
    $<$<BOOL:${ENABLE_LONG_DOUBLE_PRECISION}>:-DENABLE_LONG_DOUBLE_PRECISION=1>)
