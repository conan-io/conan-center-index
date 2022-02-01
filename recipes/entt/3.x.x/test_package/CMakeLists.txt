cmake_minimum_required(VERSION 3.8)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(EnTT REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} EnTT::EnTT)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 17 CXX_STANDARD_REQUIRED ON)
if(EnTT_VERSION VERSION_LESS "3.4.0")
  target_compile_definitions(${PROJECT_NAME} PRIVATE "ENTT_LESS_3_4_0")
endif()
