cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
if(COMPILE_AS_CPP)
  target_compile_definitions(${PROJECT_NAME} PRIVATE COMPILE_AS_CPP)
endif()
