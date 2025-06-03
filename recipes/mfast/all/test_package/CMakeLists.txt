cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(mFAST REQUIRED mfast_xml_parser CONFIG)

if(NOT TARGET fast_type_gen)
    message(FATAL_ERROR "fast_type_gen target should have been defined as part of find_package(mFAST)")
endif()

if(NOT COMMAND FASTTYPEGEN_TARGET)
    message(FATAL_ERROR "FASTTYPEGEN_TARGET should have been defined as part of find_package(mFAST)")
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(TARGET mfast_static)
  target_link_libraries(${PROJECT_NAME} PRIVATE mfast_coder_static mfast_static)
else()
  target_link_libraries(${PROJECT_NAME} PRIVATE mfast_coder mfast)
endif()
