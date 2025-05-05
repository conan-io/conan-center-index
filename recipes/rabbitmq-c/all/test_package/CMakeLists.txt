cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C)

find_package(rabbitmq-c REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(RABBITMQ_SHARED)
    target_link_libraries(${PROJECT_NAME} PRIVATE rabbitmq::rabbitmq)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE rabbitmq::rabbitmq-static)
endif()

if(WITH_SSL)
    target_compile_definitions(${PROJECT_NAME} PRIVATE WITH_SSL)
endif()

IF (rabbitmq-c_VERSION VERSION_GREATER_EQUAL "0.12.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE RABBITMQ_C_0_12_0_LATER)
    target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)
endif()
