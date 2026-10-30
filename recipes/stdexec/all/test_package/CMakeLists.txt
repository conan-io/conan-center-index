cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(stdexec REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE STDEXEC::stdexec)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
if(TARGET STDEXEC::parallel_scheduler)
    target_link_libraries(${PROJECT_NAME} PRIVATE STDEXEC::parallel_scheduler)
    target_compile_definitions(${PROJECT_NAME} PRIVATE STDEXEC_TEST_PARALLEL_SCHEDULER)
endif()
