cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(s2 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE s2::s2)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
if(MSVC)
    # Use unsigned characters
    target_compile_options(${PROJECT_NAME} PRIVATE "-J")
    target_compile_definitions(${PROJECT_NAME} PRIVATE
        # Make sure cmath header defines things like M_PI
        "_USE_MATH_DEFINES"
        # Make sure Windows doesn't define min/max macros that interfere with STL
        "NOMINMAX"
    )
endif()
