cmake_minimum_required(VERSION 3.8)

project(test_package LANGUAGES CXX)

find_package(AzureSDK CONFIG REQUIRED)

foreach(_module ${TEST_LIST})
    add_executable(test_${_module} test_${_module}.cc)
    target_link_libraries(test_${_module} PRIVATE Azure::${_module})
endforeach()
