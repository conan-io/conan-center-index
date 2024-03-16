cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(libevhtp REQUIRED CONFIG)
find_package(oniguruma REQUIRED)
find_package(Libevent REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(jemalloc REQUIRED)
find_package(gperftools REQUIRED)
add_executable(${PROJECT_NAME} example_basic.c)
target_include_directories(${PROJECT_NAME} PRIVATE
        ${libevhtp_INCLUDE_DIRS}
        ${oniguruma_INCLUDE_DIRS}
        ${Libevent_INCLUDE_DIRS}
        ${OpenSSL_INCLUDE_DIRS}
        ${jemalloc_INCLUDE_DIRS}
        ${gperftools_INCLUDE_DIRS}
)
target_link_libraries(${PROJECT_NAME} PRIVATE
        ${libevhtp_LIBRARIES}
        ${oniguruma_LIBRARIES}
        ${Libevent_LIBRARIES}
        ${OpenSSL_LIBRARIES}
        ${jemalloc_LIBRARIES}
        ${gperftools_LIBRARIES}
)
