cmake_minimum_required(VERSION 3.8)
project(test_package)

find_package(SPIRV-Tools REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_c test_package.c)
if(TARGET SPIRV-Tools-shared)
    target_link_libraries(${PROJECT_NAME}_c PRIVATE SPIRV-Tools-shared)
elseif(TARGET SPIRV-Tools-static)
    target_link_libraries(${PROJECT_NAME}_c PRIVATE SPIRV-Tools-static)
else()
    target_link_libraries(${PROJECT_NAME}_c PRIVATE SPIRV-Tools)
endif()

# TODO: we should call find_package(SPIRV-Tools-opt REQUIRED CONFIG), but not modeled right now
if(TARGET SPIRV-Tools-opt)
    add_executable(${PROJECT_NAME}_cpp test_package.cpp)
    target_link_libraries(${PROJECT_NAME}_cpp PRIVATE SPIRV-Tools-opt)
    target_compile_features(${PROJECT_NAME}_cpp PRIVATE cxx_std_11)
endif()
