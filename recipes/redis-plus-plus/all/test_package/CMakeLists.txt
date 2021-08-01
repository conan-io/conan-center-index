cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(redis++ REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
if(BUILDING_SHARED)
    target_link_libraries(${PROJECT_NAME} redis++::redis++)
else()
    target_link_libraries(${PROJECT_NAME} redis++::redis++_static)
endif()
if(BUILDING_WITH_TLS)
    target_compile_definitions(${PROJECT_NAME} PRIVATE BUILDING_WITH_TLS)
endif()

set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 11)
if(redis++_VERSION VERSION_GREATER_EQUAL "1.3.0")
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
endif()
