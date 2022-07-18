cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(userspace-rcu REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_urcu_fork.c tap.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
