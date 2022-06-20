cmake_minimum_required(VERSION 3.1)
project(test_package)

set(CMAKE_CXX_STANDARD 17)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(bs-thread-pool REQUIRED CONFIG)
find_package(Threads REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(
  ${PROJECT_NAME} PRIVATE ${CONAN_LIBS} bs-thread-pool::bs-thread-pool
                          Threads::Threads)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_${CMAKE_CXX_STANDARD})
