cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if(MSVC)
  add_definitions("-D_CRT_SECURE_NO_WARNINGS=1")
endif()

add_executable(fftsg2dt fftsg2dt.c)
target_link_libraries(fftsg2dt ${CONAN_LIBS})

add_executable(fftsg3dt fftsg3dt.c)
target_link_libraries(fftsg3dt ${CONAN_LIBS})

add_executable(shrtdctt shrtdctt.c)
target_link_libraries(shrtdctt ${CONAN_LIBS})
