cmake_minimum_required(VERSION 3.8)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

if(WITH_SSL)
  list(APPEND test_compile_definitions WITH_SSL)
endif()

target_compile_definitions(${PROJECT_NAME} PRIVATE ${test_compile_definitions})
