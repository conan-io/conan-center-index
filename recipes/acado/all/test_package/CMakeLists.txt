cmake_minimum_required(VERSION 3.10)
project(test_package CXX C)

set(CMAKE_CXX_STANDARD 11)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(ACADO REQUIRED)

add_executable(codegen codegen.cpp)
target_link_libraries(codegen PRIVATE ACADO::ACADO)

set(CODEGEN_DIR ${CMAKE_CURRENT_BINARY_DIR}/generated_code)

set(codegen_GENERATED_FILES
    ${CODEGEN_DIR}/acado_common.h
    ${CODEGEN_DIR}/acado_solver.c
    ${CODEGEN_DIR}/acado_integrator.c
    ${CODEGEN_DIR}/acado_qpoases_interface.hpp
    ${CODEGEN_DIR}/acado_qpoases_interface.cpp
    ${CODEGEN_DIR}/acado_auxiliary_functions.h
    ${CODEGEN_DIR}/acado_auxiliary_functions.c
)

add_custom_command(
  OUTPUT ${codegen_GENERATED_FILES}
  COMMAND codegen ${CODEGEN_DIR}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  DEPENDS codegen)

add_library(mpc_codegen STATIC ${codegen_GENERATED_FILES} ${ACADO_QPOASES_EMBEDDED_SOURCES})
target_include_directories(mpc_codegen
  SYSTEM PUBLIC
    ${CODEGEN_DIR}
    ${ACADO_QPOASES_EMBEDDED_INC_DIRS})

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE mpc_codegen)
