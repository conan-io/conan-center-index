cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
if(DEFINED TOMLPP_BUILD_SINGLE_ONLY AND TOMLPP_BUILD_SINGLE_ONLY)
    target_compile_definitions(${PROJECT_NAME} PRIVATE "TOMLPP_BUILD_SINGLE_ONLY")
endif()
