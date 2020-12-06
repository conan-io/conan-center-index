cmake_minimum_required(VERSION 3.0)
project(test_package)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

find_package(BISON)

set(BISON_VARS
    BISON_FOUND
    BISON_EXECUTABLE
    BISON_VERSION
)

foreach(BISON_VAR ${BISON_VARS})
    message("${BISON_VAR}: ${${BISON_VAR}}")
    if(NOT ${BISON_VAR})
        message(FATAL_ERROR "${BISON_VAR} NOT FOUND")
    endif()
endforeach()

bison_target(Bison_McParser
    mc_parser.yy "${CMAKE_CURRENT_BINARY_DIR}/mc_parser.cpp"
)

add_library(McParser STATIC
    "${CMAKE_CURRENT_BINARY_DIR}/mc_parser.cpp"
)
add_executable(${PROJECT_NAME} test_package.cpp)
set_propertY(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
