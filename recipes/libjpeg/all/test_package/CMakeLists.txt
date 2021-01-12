cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
set_property(TARGET ${PROJECT_NAME} PROPERTY C_STANDARD 99)

add_executable(test_transupp test_transupp.c "${CONAN_LIBJPEG_ROOT}/res/transupp.c")
target_link_libraries(test_transupp  ${CONAN_LIBS})
set_property(TARGET test_transupp PROPERTY C_STANDARD 99)
