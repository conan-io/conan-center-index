cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(cpptrace REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

target_link_libraries(${PROJECT_NAME} PRIVATE cpptrace::cpptrace)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

if(${cpptrace_VERSION} VERSION_GREATER_EQUAL "0.4.0")
  target_compile_definitions(${PROJECT_NAME} PRIVATE CTRACE)
endif()
