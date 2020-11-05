cmake_minimum_required(VERSION 3.13)
project(cmake_wrapper)

include(${CMAKE_CURRENT_BINARY_DIR}/../conanbuildinfo.cmake)
conan_basic_setup()

if(WIN32)
    add_definitions (-D_CRT_SECURE_NO_WARNINGS)
endif()

add_subdirectory("source_subfolder")

conan_target_link_libraries(cppbenchmark)

target_compile_features(cppbenchmark PUBLIC cxx_std_17)

install(DIRECTORY source_subfolder/include/
        DESTINATION include
        FILES_MATCHING
        PATTERN "*.h"
        PATTERN "*.inl")

if(WIN32 AND BUILD_SHARED_LIBS)
    set_target_properties(cppbenchmark PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
endif()
