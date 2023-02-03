cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

option(ENABLE_DOUBLE_PRECISION "Enable FFTW single precision" ON)
option(ENABLE_SINGLE_PRECISION "Enable FFTW single precision" OFF)
option(ENABLE_LONG_DOUBLE_PRECISION "Enable FFTW single precision" OFF)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if(ENABLE_SINGLE_PRECISION)
  find_package(FFTW3f REQUIRED CONFIG)
elseif(ENABLE_LONG_DOUBLE_PRECISION)
  find_package(FFTW3l REQUIRED CONFIG)
else()
  find_package(FFTW3 REQUIRED CONFIG)
endif()

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME}
  $<$<BOOL:${ENABLE_DOUBLE_PRECISION}>:FFTW3::fftw3>
  $<$<BOOL:${ENABLE_SINGLE_PRECISION}>:FFTW3::fftw3f>
  $<$<BOOL:${ENABLE_LONG_DOUBLE_PRECISION}>:FFTW3::fftw3l>)

target_compile_options(${PROJECT_NAME} PRIVATE
    $<$<BOOL:${ENABLE_SINGLE_PRECISION}>:-DENABLE_SINGLE_PRECISION=1>
    $<$<BOOL:${ENABLE_LONG_DOUBLE_PRECISION}>:-DENABLE_LONG_DOUBLE_PRECISION=1>)
