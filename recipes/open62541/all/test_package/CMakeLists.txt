cmake_minimum_required(VERSION 2.8.11)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Threads)

add_executable(${PROJECT_NAME}_server test_server_package.c)
target_link_libraries(${PROJECT_NAME}_server ${CONAN_LIBS} ${CMAKE_DL_LIBS} ${CMAKE_THREAD_LIBS_INIT})

add_executable(${PROJECT_NAME}_client test_client_package.c)
target_link_libraries(${PROJECT_NAME}_client ${CONAN_LIBS} ${CMAKE_DL_LIBS} ${CMAKE_THREAD_LIBS_INIT})
