cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(imgui REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE imgui::imgui)
if (DOCKING)
    target_compile_definitions(${PROJECT_NAME} PRIVATE -DDOCKING)
endif()
target_compile_definitions(${PROJECT_NAME} PUBLIC "IMGUI_USER_CONFIG=\"${CMAKE_CURRENT_SOURCE_DIR}/my_imgui_config.h\"")
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
