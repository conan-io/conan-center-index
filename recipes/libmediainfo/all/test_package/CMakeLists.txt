cmake_minimum_required(VERSION 2.8.12)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

option(LIBMEDIAINFO_SHARED "Is libmediainfo a shared library?")
if(LIBMEDIAINFO_SHARED)
    target_compile_definitions(${PROJECT_NAME} PRIVATE LIBMEDIAINFO_SHARED)
endif()
