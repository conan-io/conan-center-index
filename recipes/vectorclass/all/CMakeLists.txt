cmake_minimum_required(VERSION 3.8)
project(vectorclass LANGUAGES CXX)

file(GLOB HEADERS "${VECTORCLASS_SRC_DIR}/*.h")

add_library(vectorclass STATIC ${VECTORCLASS_SRC_DIR}/instrset_detect.cpp)
target_compile_features(vectorclass PUBLIC cxx_std_17)
set_target_properties(vectorclass PROPERTIES PUBLIC_HEADER "${HEADERS}")

include(GNUInstallDirs)
install(TARGETS vectorclass
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
