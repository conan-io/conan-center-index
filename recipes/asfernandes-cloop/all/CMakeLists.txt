cmake_minimum_required(VERSION 3.1)

project(cloop CXX)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

# ---- cloop executable ----

add_executable(
    cloop
    src/cloop/Expr.cpp
    src/cloop/Generator.cpp
    src/cloop/Lexer.cpp
    src/cloop/Main.cpp
    src/cloop/Parser.cpp
    src/cloop/Expr.h
    src/cloop/Generator.h
    src/cloop/Lexer.h
    src/cloop/Parser.h
)

# ---- Install rules ----

include(GNUInstallDirs)
install(TARGETS cloop RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}")
