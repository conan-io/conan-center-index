cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

find_package(onnxruntime REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(WITH_CUDA)
  target_compile_definitions(${PROJECT_NAME} PRIVATE WITH_CUDA)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE onnxruntime::onnxruntime)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
