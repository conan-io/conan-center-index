cmake_minimum_required(VERSION 3.15)
project(Lemon LANGUAGES C)

add_executable(lemon ${LEMON_SRC_DIR}/tool/lemon.c)

include(GNUInstallDirs)
install(TARGETS lemon DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES ${LEMON_SRC_DIR}/tool/lempar.c DESTINATION ${CMAKE_INSTALL_BINDIR})
