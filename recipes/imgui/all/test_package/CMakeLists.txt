cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(imgui REQUIRED CONFIG)

add_compile_definitions("IMGUI_USER_CONFIG=\"${CMAKE_CURRENT_SOURCE_DIR}/my_imgui_config.h\"")
add_executable(${PROJECT_NAME} test_package.cpp)
# Using the aggregate target for easier testing.
target_link_libraries(${PROJECT_NAME} PRIVATE imgui::imgui_all)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

if(APPLE)
    enable_language(OBJCXX)
    add_executable(${PROJECT_NAME}_objcxx test_package.mm)
    target_link_libraries(${PROJECT_NAME}_objcxx PRIVATE imgui::imgui_all)
    target_compile_features(${PROJECT_NAME}_objcxx PRIVATE cxx_std_11)
endif()
