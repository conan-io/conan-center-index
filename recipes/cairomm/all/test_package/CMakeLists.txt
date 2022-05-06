cmake_minimum_required(VERSION 3.6)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGET)

find_package(PkgConfig REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)

pkg_search_module(CAIROMM IMPORTED_TARGET cairomm-1.16)
if (TARGET PkgConfig::CAIROMM)
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
else()
  pkg_search_module(CAIROMM IMPORTED_TARGET REQUIRED cairomm-1.0)
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
endif()

target_link_libraries(${PROJECT_NAME} PkgConfig::CAIROMM)
