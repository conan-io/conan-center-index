cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(thorvg REQUIRED CONFIG)

find_package(OpenMP)
if(OpenMP_CXX_FOUND)
    set(OPENMP_DEP OpenMP::OpenMP_CXX)
else()
    set(OPENMP_DEP "")
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE thorvg::thorvg ${OPENMP_DEP})
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
