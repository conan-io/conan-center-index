cmake_minimum_required(VERSION 3.0)
project(cmake_wrapper)

include(${CONAN_INSTALL_FOLDER}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if(APPLE)
    cmake_minimum_required(VERSION 3.16)
    enable_language(OBJC)
    set(CMAKE_OBJC_FLAGS "${CMAKE_OBJC_FLAGS} ${CMAKE_C_FLAGS}")
endif()

add_subdirectory(source_subfolder)
