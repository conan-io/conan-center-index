cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(SPIRV-Tools REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c PRIVATE SPIRV-Tools)

# TODO: we should call find_package(SPIRV-Tools-opt REQUIRED CONFIG), but not modeled right now
add_executable(${PROJECT_NAME}_cpp test_package.cpp)
target_link_libraries(${PROJECT_NAME}_cpp PRIVATE SPIRV-Tools-opt)
if(SPIRV-Tools_VERSION VERSION_LESS "1.3.243.0")
    target_compile_features(${PROJECT_NAME}_cpp PRIVATE cxx_std_11)
else()
    target_compile_features(${PROJECT_NAME}_cpp PRIVATE cxx_std_17)
endif()
