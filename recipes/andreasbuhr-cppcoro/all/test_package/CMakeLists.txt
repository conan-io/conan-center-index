cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
  target_compile_options(${PROJECT_NAME} PRIVATE -fcoroutines)
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
  target_compile_options(${PROJECT_NAME}, PRIVATE -fcoroutines-ts)
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
  # Lower version MSVC/Visual Studio still requires /await to support coroutines, despite having /std:c++latest
  target_compile_options(${PROJECT_NAME} PRIVATE /await)
endif()
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 20)
