cmake_minimum_required(VERSION 2.8.12)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

function(add_option option)
    if(${option})
        target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE "${option}")
    endif()
endfunction()

add_option(WITH_X11)
add_option(WITH_ALSA)
add_option(WITH_PULSE)
add_option(WITH_ESD)
add_option(WITH_ARTS)
add_option(WITH_DIRECTFB)
add_option(WITH_DIRECTX)
