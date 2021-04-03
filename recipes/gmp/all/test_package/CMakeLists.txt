cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

if (TEST_PIC)
    add_library(${PROJECT_NAME}_shared SHARED test_package.c)
    target_link_libraries(${PROJECT_NAME}_shared ${CONAN_LIBS})
endif()

if (ENABLE_CXX)
    add_executable(${PROJECT_NAME}_cpp test_package.cpp)
    target_link_libraries(${PROJECT_NAME}_cpp ${CONAN_LIBS})
endif()
