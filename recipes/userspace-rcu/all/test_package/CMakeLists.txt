cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(userspace-rcu COMPONENTS urcu REQUIRED)

set(TEST_SRC test_urcu_fork.c tap.c)

add_executable(${PROJECT_NAME} ${TEST_SRC})
target_link_libraries(${PROJECT_NAME} userspace-rcu::urcu)

add_executable(${PROJECT_NAME}-mb ${TEST_SRC})
target_link_libraries(${PROJECT_NAME}-mb userspace-rcu::urcu-mb)

add_executable(${PROJECT_NAME}-signal ${TEST_SRC})
target_link_libraries(${PROJECT_NAME}-signal userspace-rcu::urcu-signal)
