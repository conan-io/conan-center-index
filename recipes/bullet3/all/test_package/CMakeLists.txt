cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(Bullet REQUIRED CONFIG)
include(${BULLET_ROOT_DIR}/${BULLET_USE_FILE})

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${BULLET_LIBRARIES})
