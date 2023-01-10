cmake_minimum_required(VERSION 3.1)
project(test_package)

# Find FLEX before `conanbuildinfo.cmake` because that file will let `find_program`
# look for  executables in host packages (let's hope conan 2.0 fixes this)
find_package(FLEX REQUIRED)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(FLEX REQUIRED)

flex_target(flex_scanner basic_nr.l "${PROJECT_BINARY_DIR}/basic_nr.cpp")

add_executable(${PROJECT_NAME} basic_nr.cpp)
target_include_directories(${PROJECT_NAME} PRIVATE ${FLEX_INCLUDE_DIRS})
target_link_libraries(${PROJECT_NAME} PRIVATE ${FLEX_LIBRARIES})

add_executable(test_yywrap test_yywrap.c)
target_link_libraries(test_yywrap PRIVATE ${FLEX_LIBRARIES})
