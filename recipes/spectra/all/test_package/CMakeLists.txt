cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(spectra REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Spectra::Spectra)
if(spectra_VERSION VERSION_LESS "1.0.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE "SPECTRA_LESS_1_0_0")
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
endif()
