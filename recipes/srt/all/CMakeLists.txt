cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(CONAN_LIBS_PTHREADS4W)
    set(PTHREAD_LIBRARY "${CONAN_LIBS_PTHREADS4W}")
    set(PTHREAD_INCLUDE_DIR "${CONAN_INCLUDE_DIRS_PTHREADS4W}")
endif()

add_subdirectory("source_subfolder")
