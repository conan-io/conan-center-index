cmake_minimum_required(VERSION 2.8.12)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(HEADER_FILES    calculator_constants.h
                    calculator_types.h
                    Calculator.h)

set(SOURCE_FILES    calculator_constants.cpp
                    calculator_types.cpp
                    Calculator.cpp
                    test_package.cpp)

add_executable(${PROJECT_NAME} ${SOURCE_FILES} ${HEADER_FILES})
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 11)
