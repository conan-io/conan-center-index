cmake_minimum_required(VERSION 3.15)

project(test_package CXX) # if the project uses c++

find_package(whisper-cpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE whisper-cpp::whisper-cpp)


add_custom_command(TARGET test_package POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${whisper-cpp_INCLUDE_DIR}/../res/models
        ${CMAKE_CURRENT_BINARY_DIR}/models)
