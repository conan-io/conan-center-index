cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(SPIRV-Tools REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_c test_package.c)
if(TARGET SPIRV-Tools-shared)
    target_link_libraries(${PROJECT_NAME}_c SPIRV-Tools-shared)
elseif(TARGET SPIRV-Tools-static)
    target_link_libraries(${PROJECT_NAME}_c SPIRV-Tools-static)
else()
    target_link_libraries(${PROJECT_NAME}_c SPIRV-Tools)
endif()

# TODO: we should call find_package(SPIRV-Tools-opt REQUIRED CONFIG), but not modeled right now
if(TARGET SPIRV-Tools-opt)
    add_executable(${PROJECT_NAME}_cpp test_package.cpp)
    target_link_libraries(${PROJECT_NAME}_cpp SPIRV-Tools-opt)
    set_property(TARGET ${PROJECT_NAME}_cpp PROPERTY CXX_STANDARD 11)
endif()
