cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module Development.Embed)

message("Python3_EXECUTABLE: ${Python3_EXECUTABLE}")
message("Python3_INTERPRETER_ID: ${Python3_INTERPRETER_ID}")
message("Python3_VERSION: ${Python3_VERSION}")
message("Python3_INCLUDE_DIRS: ${Python3_INCLUDE_DIRS}")
message("Python3_LIBRARIES: ${Python3_LIBRARIES}")

option(BUILD_MODULE "Build python module")
if(BUILD_MODULE)
    python3_add_library(spam "test_module.c")
    if(MSVC)
        set_target_properties(spam PROPERTIES DEBUG_POSTFIX "_d")
    endif()
endif()

add_executable(${PROJECT_NAME} "test_package.c")
target_link_libraries(${PROJECT_NAME} PRIVATE Python3::Python)
