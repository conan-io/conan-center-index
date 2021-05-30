cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(fastcdr REQUIRED)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# check if the alias target fastcdr works 
add_executable(${PROJECT_NAME}_1 test_package.cpp)
target_link_libraries(${PROJECT_NAME}_1
    fastcdr
)

# check if the normal target name with namespace works
add_executable(${PROJECT_NAME}_2 test_package.cpp)
target_link_libraries(${PROJECT_NAME}_2
    fastcdr::fastcdr
)
