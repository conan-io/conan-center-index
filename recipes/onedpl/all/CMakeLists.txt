cmake_minimum_required(VERSION 3.4.3)
project(cmake_wrapper)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if(TARGET CONAN_PKG::tbb)
    if(NOT TARGET TBB::tbb)
        add_library(TBB::tbb IMPORTED INTERFACE)
        target_link_libraries(TBB::tbb INTERFACE CONAN_PKG::tbb)
    endif()
endif()

add_subdirectory("source_subfolder")
