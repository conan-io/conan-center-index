cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(dice-template-library REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE dice-template-library::dice-template-library)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)

if(dice-template-library_VERSION VERSION_GREATER_EQUAL "1.0.0")
  target_compile_definitions(${PROJECT_NAME} PRIVATE DICE_TEMPLATE_LIBRARY_1_0_0_LATER)
endif()
