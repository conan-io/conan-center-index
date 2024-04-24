cmake_minimum_required(VERSION 3.12)
project(test_package C)

find_package(open62541 REQUIRED CONFIG)
find_package(Threads REQUIRED)

add_executable(${PROJECT_NAME}
    ../test_package/test_package.c
)

target_link_libraries(${PROJECT_NAME} PRIVATE open62541::open62541)
