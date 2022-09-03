cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(SDL2 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE SDL2::SDL2main)
if(TARGET SDL2::SDL2-static)
    target_link_libraries(${PROJECT_NAME} PRIVATE SDL2::SDL2-static)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE SDL2::SDL2)
endif()

function(add_option option)
    if(${option})
        target_compile_definitions(${PROJECT_NAME} PRIVATE "${option}")
    endif()
endfunction()

add_option(WITH_X11)
add_option(WITH_ALSA)
add_option(WITH_PULSE)
add_option(WITH_ESD)
add_option(WITH_ARTS)
add_option(WITH_DIRECTFB)
add_option(WITH_DIRECTX)
