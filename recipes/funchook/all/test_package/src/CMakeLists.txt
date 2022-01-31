cmake_minimum_required(VERSION 3.1)
SET(SOURCES test_package.c)

ADD_EXECUTABLE(${CMAKE_PROJECT_NAME} ${SOURCES})

conan_target_link_libraries(${CMAKE_PROJECT_NAME})
