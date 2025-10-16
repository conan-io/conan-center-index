cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C CXX)

find_package(nvtx REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_c test_package.c)
target_compile_features(${PROJECT_NAME}_c PRIVATE c_std_99)
target_link_libraries(${PROJECT_NAME}_c PRIVATE nvtx::nvtx)

add_executable(${PROJECT_NAME}_cxx test_package.cpp)
target_link_libraries(${PROJECT_NAME}_cxx PRIVATE nvtx::nvtx)

# This is for backwards compatibility only
if(NVTX_3_0_1)
  add_compile_definitions(NVTX_3_0_1)
endif()


