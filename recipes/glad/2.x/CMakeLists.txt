cmake_minimum_required(VERSION 3.12)
project(glad)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/src/cmake")

include(GladConfig)

glad_add_library(glad
    ${GLAD_CONAN_LOADER}
    ${GLAD_CONAN_DEBUG}
    ${GLAD_CONAN_MX}
    ${GLAD_CONAN_LIB_TYPE}
    LANGUAGE C
    API ${GLAD_CONAN_API}
    EXTENSIONS ${GLAD_CONAN_EXTENSIONS}
)

install(TARGETS glad)
install(DIRECTORY ${CMAKE_BINARY_DIR}/gladsources/glad/include/ TYPE INCLUDE)
