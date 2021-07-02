cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Thrift CONFIG REQUIRED)

set(HEADER_FILES    calculator_constants.h
                    calculator_types.h
                    Calculator.h)

set(SOURCE_FILES    calculator_constants.cpp
                    calculator_types.cpp
                    Calculator.cpp
                    test_package.cpp)

add_executable(${PROJECT_NAME} ${SOURCE_FILES} ${HEADER_FILES})
target_link_libraries(${PROJECT_NAME} thriftnb::thriftnb)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 11)
