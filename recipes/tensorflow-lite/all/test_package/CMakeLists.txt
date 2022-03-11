cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
find_package(tensorflowlite REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example PRIVATE tensorflow::tensorflowlite)
file(COPY ${CMAKE_CURRENT_LIST_DIR}/model.tflite DESTINATION ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})

