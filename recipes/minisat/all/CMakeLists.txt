cmake_minimum_required(VERSION 3.8)

project(MiniSat CXX)

find_package(ZLIB CONFIG REQUIRED)
include_directories(SYSTEM ${ZLIB_INCLUDE_DIR})

# no Main.cc as these are the command line tools
file(GLOB SRC minisat/core/Solver.cc minisat/simp/SimpSolver.cc minisat/utils/*.cc)
add_library(minisat ${SRC})
target_include_directories(minisat PUBLIC .)

install(TARGETS minisat PUBLIC_HEADER DESTINATION minisat)
INSTALL (
    DIRECTORY ${CMAKE_SOURCE_DIR}/
    DESTINATION include
    FILES_MATCHING PATTERN "*.h*")
