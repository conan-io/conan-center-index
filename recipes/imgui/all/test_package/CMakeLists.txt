cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(imgui REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE imgui::imgui)

option(DOCKING "Test docking" OFF)

if (DOCKING)
    target_compile_definitions(${PROJECT_NAME} PRIVATE -DDOCKING)
endif()

if(ENABLE_TEST_ENGINE)
    target_compile_definitions(${PROJECT_NAME} PRIVATE -DENABLE_TEST_ENGINE)
endif()

if(USE_WCHAR32)
    target_compile_definitions(${PROJECT_NAME} PRIVATE -DUSE_WCHAR32)
endif()

target_compile_definitions(${PROJECT_NAME} PUBLIC "IMGUI_USER_CONFIG=\"${CMAKE_CURRENT_SOURCE_DIR}/my_imgui_config.h\"")
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
