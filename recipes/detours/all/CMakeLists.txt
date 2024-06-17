cmake_minimum_required(VERSION 3.12)
project(conan_detours CXX)

set(SOURCES_DIR ${CMAKE_CURRENT_LIST_DIR}/src)

file(GLOB DETOURS_SOURCES ${SOURCES_DIR}/src/*.cpp)
list(REMOVE_ITEM DETOURS_SOURCES
    "${SOURCES_DIR}/src/uimports.cpp"
)
file(GLOB DETOURS_HEADERS ${SOURCES_DIR}/src/*.h)
add_library(detours STATIC ${DETOURS_SOURCES} ${DETOURS_HEADERS})

include(GNUInstallDirs)
install(TARGETS detours)
install(FILES ${DETOURS_HEADERS} DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}")
