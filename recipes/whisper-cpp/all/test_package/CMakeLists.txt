cmake_minimum_required(VERSION 3.15)

project(test_package CXX) # if the project uses c++

find_package(whisper-cpp REQUIRED CONFIG)
find_package(drwav REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
# don't link to ${CONAN_LIBS} or CONAN_PKG::package
target_link_libraries(${PROJECT_NAME} PRIVATE whisper-cpp::whisper-cpp drwav::drwav)

add_custom_command(TARGET test_package POST BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_CURRENT_SOURCE_DIR}/jfkmoon.wav
        $<TARGET_FILE_DIR:test_package>)