cmake_minimum_required(VERSION 2.8.12)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

file(GLOB SOURCE_FILES *.cpp)

add_executable(${PROJECT_NAME} ${SOURCE_FILES})
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
