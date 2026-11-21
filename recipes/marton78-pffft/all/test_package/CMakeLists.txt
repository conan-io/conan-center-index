cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(pffft REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE PFFFT::PFFFT)

if(PFFFT_WITH_FLOAT)
    target_compile_definitions(${PROJECT_NAME} PRIVATE TEST_FLOAT)
endif()
if(PFFFT_WITH_PFFASTCONV)
    target_link_libraries(${PROJECT_NAME} PRIVATE PFFFT::PFFASTCONV)
    target_compile_definitions(${PROJECT_NAME} PRIVATE TEST_PFFASTCONV)
endif()
if(PFFFT_WITH_PFDSP)
    target_link_libraries(${PROJECT_NAME} PRIVATE PFFFT::PFDSP)
    target_compile_definitions(${PROJECT_NAME} PRIVATE TEST_PFDSP)
endif()
