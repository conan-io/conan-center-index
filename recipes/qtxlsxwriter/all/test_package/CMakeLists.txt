cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME} example.cpp)

target_include_directories(${PROJECT_NAME} PRIVATE ${CONAN_INCLUDE_DIRS})
target_link_directories(${PROJECT_NAME} PRIVATE ${CONAN_LIB_DIRS})

# place qt::Gui before qt::Core (important for some toolchains)
# since the current qt recipe provides an incorrect order of libraries
target_link_libraries(${PROJECT_NAME}
    Qt5Gui
    ${CONAN_LIBS}
)

# `fPIC` option must be used because qt was built with `reduce-relocations`
target_compile_options(${PROJECT_NAME} PRIVATE -fPIC)
