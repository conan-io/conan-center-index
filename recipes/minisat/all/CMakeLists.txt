cmake_minimum_required(VERSION 3.15)
project(minisat LANGUAGES CXX)

find_package(ZLIB REQUIRED)

# no Main.cc as these are the command line tools
add_library(minisat
    ${MINISAT_SRC_DIR}/core/Solver.cc
    ${MINISAT_SRC_DIR}/simp/SimpSolver.cc
    ${MINISAT_SRC_DIR}/utils/Options.cc
    ${MINISAT_SRC_DIR}/utils/System.cc
)
target_include_directories(minisat PUBLIC ${MINISAT_SRC_DIR})
target_link_libraries(minisat PUBLIC ZLIB::ZLIB)
set_target_properties(minisat PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)

include(GNUInstallDirs)
install(
    TARGETS minisat
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(DIRECTORY ${MINISAT_SRC_DIR}/mtl ${MINISAT_SRC_DIR}/utils ${MINISAT_SRC_DIR}/core ${MINISAT_SRC_DIR}/simp
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/minisat
    FILES_MATCHING PATTERN "*.h"
)
