cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(ANTLR3 REQUIRED CONFIG)
if(WIN32)
    find_program(ANTLR3_EXECUTABLE antlr3.bat REQUIRED)
else()
    find_program(ANTLR3_EXECUTABLE antlr3 REQUIRED)
endif()

set(GEN ${CMAKE_CURRENT_BINARY_DIR}/gen)
add_custom_command(
    OUTPUT ${GEN}/ExprLexer.cpp ${GEN}/ExprParser.cpp ${GEN}/ExprLexer.hpp ${GEN}/ExprParser.hpp
    COMMAND ${CMAKE_COMMAND} -E make_directory ${GEN}
    COMMAND ${ANTLR3_EXECUTABLE} -fo ${GEN} ${CMAKE_CURRENT_SOURCE_DIR}/Expr.g
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/Expr.g
    COMMENT "ANTLR3 Expr.g")

add_executable(${PROJECT_NAME} test_package.cpp ${GEN}/ExprLexer.cpp ${GEN}/ExprParser.cpp)
target_include_directories(${PROJECT_NAME} PRIVATE ${GEN})
target_link_libraries(${PROJECT_NAME} PRIVATE ANTLR3::antlr3)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
