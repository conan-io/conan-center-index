cmake_minimum_required(VERSION 3.9)
project(PackageTest)

set(CMAKE_CXX_STANDARD 17)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
# the following is not working in the toolkit v26
#conan_basic_setup(TARGETS)
find_package(ncbi-cxx-toolkit-public REQUIRED)

NCBI_begin_app(basic_sample)
  NCBI_sources(basic_sample)
  NCBI_uses_toolkit_libraries(xncbi)
NCBI_end_app()

add_executable(basic_sample2 basic_sample.cpp)
target_link_libraries(basic_sample2 ${CONAN_LIBS})

