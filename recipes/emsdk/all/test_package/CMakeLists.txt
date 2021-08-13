cmake_minimum_required(VERSION 3.18.2)
project(test_package)

option(USE_CONANBUILDINFO "Use conanbuildinfo.cmake")

if(USE_CONANBUILDINFO)
    include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
    conan_basic_setup()
else()
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY bin)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
