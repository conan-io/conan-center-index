CMAKE_MINIMUM_REQUIRED(VERSION 3.15)

PROJECT(test_package LANGUAGES CXX)

find_package(qtils  CONFIG REQUIRED)

add_executable(${PROJECT_NAME}
        test_package.cpp
)

target_link_libraries(${PROJECT_NAME} PRIVATE
        qtils::qtils
)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
