cmake_minimum_required(VERSION 3.1)

project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
find_package(CUDASDK REQUIRED)
enable_language(CUDA)
add_executable(${PROJECT_NAME} test_package.cu)
target_link_libraries(${PROJECT_NAME} PRIVATE CUDASDK::cudart_static)
