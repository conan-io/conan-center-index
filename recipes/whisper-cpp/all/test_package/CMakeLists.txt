cmake_minimum_required(VERSION 3.15)

project(test_package CXX) # if the project uses c++

find_package(whisper-cpp REQUIRED CONFIG)
find_package(Threads REQUIRED)
if (THREADS_PREFER_PTHREAD_FLAG)
    set(CMAKE_C_FLAGS   "${CMAKE_C_FLAGS}   -pthread")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
# don't link to ${CONAN_LIBS} or CONAN_PKG::package
target_link_libraries(${PROJECT_NAME} PRIVATE whisper-cpp::whisper-cpp)


add_custom_command(TARGET test_package POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${whisper-cpp_INCLUDE_DIR}/../res/models
        ${CMAKE_CURRENT_BINARY_DIR}/models)
