cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(mdspan REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE std::mdspan)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_14)

if(mdspan_VERSION VERSION_GREATER_EQUAL "0.2.0")
  target_compile_definitions(${PROJECT_NAME} PRIVATE "MDSPAN_ENABLE_SUBMDSPAN")
endif()
