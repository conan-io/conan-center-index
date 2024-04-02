cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(Libjwt REQUIRED CONFIG)
find_package(OpenSSL REQUIRED)
find_package(jansson REQUIRED)
add_executable(${PROJECT_NAME} example_basic.c)
target_include_directories(${PROJECT_NAME} PRIVATE
        ${jansson_INCLUDE_DIRS}
        ${OpenSSL_INCLUDE_DIRS}
        ${Libjwt_INCLUDE_DIRS}
)
target_link_libraries(${PROJECT_NAME} PRIVATE
        ${jansson_LIBRARIES}
        ${OpenSSL_LIBRARIES}
        ${Libjwt_LIBRARIES}
)
