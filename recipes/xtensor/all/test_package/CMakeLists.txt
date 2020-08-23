cmake_minimum_required(VERSION 2.8.12)
project(test_package CXX)

include(CheckCXXCompilerFlag)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 14)

foreach(flag "-march=native" "-mtune=native")
  check_cxx_compiler_flag(${flag} COMPILER_SUPPORTS_MARCH_NATIVE)
  if(COMPILER_SUPPORTS_MARCH_NATIVE)
    target_compile_options(${PROJECT_NAME} PRIVATE ${flag})
  endif()
endforeach()
