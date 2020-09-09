cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

include(FindPkgConfig)
pkg_check_modules(libmodman REQUIRED IMPORTED_TARGET libmodman-2.0)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::libmodman)
set_propertY(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)

add_library(test_module1 MODULE test_module1.cpp)
set_target_properties(test_module1 PROPERTIES PREFIX "")
target_include_directories(test_module1 PRIVATE ${libmodman_INCLUDE_DIRS})
set_property(TARGET test_module1 PROPERTY CXX_VISIBILITY_PRESET hidden)
set_propertY(TARGET test_module1 PROPERTY CXX_STANDARD 11)

add_library(test_module2 MODULE test_module2.cpp)
set_target_properties(test_module2 PROPERTIES PREFIX "")
target_include_directories(test_module2 PRIVATE ${libmodman_INCLUDE_DIRS})
set_property(TARGET test_module2 PROPERTY CXX_VISIBILITY_PRESET hidden)
set_propertY(TARGET test_module2 PROPERTY CXX_STANDARD 11)
