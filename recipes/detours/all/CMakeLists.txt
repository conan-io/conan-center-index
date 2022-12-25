cmake_minimum_required(VERSION 3.0)
project(conan_detours CXX)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

file(GLOB DETOURS_SOURCES source_subfolder/src/*.cpp)
list(REMOVE_ITEM DETOURS_SOURCES
    "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/uimports.cpp"
)
file(GLOB DETOURS_HEADERS source_subfolder/src/*.h)
add_library(detours STATIC ${DETOURS_SOURCES} ${DETOURS_HEADERS})

include(GNUInstallDirs)
install(TARGETS detours
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
)
install(FILES ${DETOURS_HEADERS} DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}")
