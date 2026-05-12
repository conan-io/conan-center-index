cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(CLBlast CONFIG REQUIRED)
find_package(OpenCLHeaders REQUIRED)
find_package(OpenCLHeadersCpp REQUIRED)

if(APPLE)
  set(OPENCL_LIBS "-framework OpenCL")
else()
  find_package(OpenCLICDLoader REQUIRED)
  set(OPENCL_LIBS OpenCL::OpenCL)
endif()

add_executable(example src/example.cpp)

target_link_libraries(example PRIVATE
    clblast::clblast
    OpenCL::HeadersCpp
    OpenCL::Headers
    ${OPENCL_LIBS}
)
