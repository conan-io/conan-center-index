cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(libraw REQUIRED CONFIG)

# libraw/0.19.5 uses std::auto_ptr 
if (libraw_VERSION VERSION_EQUAL "0.19.5")
    set(CMAKE_CXX_STANDARD 11)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE libraw::libraw)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
