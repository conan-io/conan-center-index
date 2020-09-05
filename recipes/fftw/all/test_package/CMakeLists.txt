cmake_minimum_required(VERSION 3.1)
project(test_package)

option(ENABLE_SINGLE_PRECISION "Enable FFTW single precision" OFF)
option(ENABLE_LONG_DOUBLE_PRECISION "Enable FFTW single precision" OFF)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(FFTW3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} FFTW3::fftw3)

target_compile_options(${PROJECT_NAME} PRIVATE
    $<$<BOOL:${ENABLE_SINGLE_PRECISION}>:-DENABLE_SINGLE_PRECISION=1>
    $<$<BOOL:${ENABLE_LONG_DOUBLE_PRECISION}>:-DENABLE_LONG_DOUBLE_PRECISION=1>)
