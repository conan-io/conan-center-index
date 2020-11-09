cmake_minimum_required(VERSION 3.1)
project(mongo-c-driver-tester C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if(MONGO-C-DRIVER_SHARED)
    message(STATUS "Testing shared mongoc")
else()
    message(STATUS "Testing static mongoc")
    add_definitions (-DBSON_STATIC)
    add_definitions (-DMONGOC_STATIC)
endif()

add_executable(${PROJECT_NAME} tester.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
