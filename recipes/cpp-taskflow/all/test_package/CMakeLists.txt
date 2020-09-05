cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CPPTASKFLOW_CXX_STANDARD 14)
if (CPPTASKFLOW_VERSION LESS_EQUAL "2.2.0")
    set(CPPTASKFLOW_CXX_STANDARD 17)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD ${CPPTASKFLOW_CXX_STANDARD})
