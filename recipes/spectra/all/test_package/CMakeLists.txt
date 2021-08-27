cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(spectra REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} Spectra::Spectra)
if(spectra_VERSION VERSION_LESS "1.0.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE "SPECTRA_LESS_1_0_0")
else()
    set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
endif()
