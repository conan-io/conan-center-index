cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME} test_package.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)

set(WT_COMPONENTS Wt HTTP)
set(WT_TARGETS Wt::Wt Wt::HTTP)
if(WITH_DBO)
    target_compile_definitions(${PROJECT_NAME} PRIVATE WITH_DBO)
    list(APPEND WT_COMPONENTS Dbo)
    list(APPEND WT_TARGETS Wt::Dbo)
endif()

find_package(wt REQUIRED ${WT_COMPONENTS} CONFIG)
target_link_libraries(${PROJECT_NAME} PRIVATE ${WT_TARGETS})
