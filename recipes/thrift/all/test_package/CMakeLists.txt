cmake_minimum_required(VERSION 3.1)
project(test_package)

include("${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake")
conan_basic_setup()

option(THRIFT_COMPILER_AVAILABLE "Thrift compiler is available")

add_executable(${PROJECT_NAME} test_package.cpp calc.thrift)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
target_include_directories(${PROJECT_NAME} PRIVATE "${CMAKE_BINARY_DIR}")


set(THRIFT_SRCS
    "${CMAKE_BINARY_DIR}/shared_types.cpp"
    "${CMAKE_BINARY_DIR}/SharedService.cpp"
    "${CMAKE_BINARY_DIR}/calc_types.cpp"
    "${CMAKE_BINARY_DIR}/Calculator.cpp"
)

if(USE_CXX_11)
    set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
else()
    set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 98)
endif()


if(THRIFT_COMPILER_AVAILABLE)
    add_custom_command(
        OUTPUT ${THRIFT_SRCS}
        COMMAND ${CONAN_BIN_DIRS_THRIFT}/thrift -r -I ${CMAKE_SOURCE_DIR} -out ${CMAKE_CURRENT_BINARY_DIR} --gen cpp ${CMAKE_SOURCE_DIR}/calc.thrift 
        DEPENDS calc.thrift
        COMMENT "Generating thrift sources"
    )

endif()

target_sources(${PROJECT_NAME} PRIVATE
    "${CMAKE_BINARY_DIR}/shared_types.cpp"
    "${CMAKE_BINARY_DIR}/SharedService.cpp"
    "${CMAKE_BINARY_DIR}/calc_types.cpp"
    "${CMAKE_BINARY_DIR}/Calculator.cpp"
)
