cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(imgui REQUIRED)

set(CMAKE_CXX_STANDARD 11)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} imgui::imgui)
if (DOCKING)
    target_compile_definitions(${PROJECT_NAME} PRIVATE -DDOCKING)
endif()
target_compile_definitions(${PROJECT_NAME} PUBLIC "IMGUI_USER_CONFIG=\"${CMAKE_CURRENT_SOURCE_DIR}/my_imgui_config.h\"")
