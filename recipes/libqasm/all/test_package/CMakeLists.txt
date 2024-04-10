cmake_minimum_required(VERSION 3.12)

project(PackageTest CXX)

find_package(libqasm REQUIRED CONFIG)

add_executable(test_package
    "${CMAKE_CURRENT_SOURCE_DIR}/src/test_package.cpp"
)
target_compile_features(test_package PRIVATE cxx_std_20)
if(MSVC)
    target_compile_options(test_package PRIVATE /DEBUG:NONE)
endif()
target_link_libraries(test_package PRIVATE libqasm::libqasm)
