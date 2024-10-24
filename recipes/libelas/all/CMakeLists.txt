# Adapted from the original CMakeLists.txt
# mirror: https://github.com/kou1okada/libelas/blob/master/CMakeLists.txt

cmake_minimum_required(VERSION 3.15)
project(libelas LANGUAGES CXX)

if(USE_SSE3)
    if(MSVC)
        add_compile_options(/arch:SSE3)
    else()
        add_compile_options(-msse3)
    endif()
endif()

find_package(OpenMP REQUIRED)

add_library(elas
    descriptor.cpp
    elas.cpp
    filter.cpp
    matrix.cpp
    triangle.cpp
)

target_link_libraries(elas PRIVATE OpenMP::OpenMP_CXX)

install(TARGETS elas
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)
install(FILES elas.h DESTINATION include)
