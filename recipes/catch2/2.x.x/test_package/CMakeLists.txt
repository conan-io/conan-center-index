cmake_minimum_required(VERSION 3.5)
project(test_package)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} 000-CatchMain.cpp 100-Fix-Section.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
