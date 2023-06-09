cmake_minimum_required(VERSION 3.15)
project(test_DrLibs LANGUAGES CXX) # if the project uses c++

find_package(dr_libs REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE dr_libs::dr_libs)

add_custom_command(TARGET test_DrLibs POST_BUILD        # Adds a post-build event to MyTest
        COMMAND ${CMAKE_COMMAND} -E copy_if_different  # which executes "cmake - E copy_if_different..."
        "${CMAKE_CURRENT_SOURCE_DIR}/sample.wav"      # <--this is in-file
        $<TARGET_FILE_DIR:test_DrLibs>)