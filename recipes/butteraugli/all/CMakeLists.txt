cmake_minimum_required(VERSION 3.8)
project(butteraugli LANGUAGES CXX)

option(BUTTERAUGLI_TOOL "Build comparison tool" ON)

add_library(butteraugli_lib ${BUTTERAUGLI_SRC_DIR}/butteraugli/butteraugli.cc)
target_include_directories(butteraugli_lib PUBLIC ${BUTTERAUGLI_SRC_DIR})
set_target_properties(butteraugli_lib PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
target_compile_features(butteraugli_lib PUBLIC cxx_std_11)

install(
    TARGETS butteraugli_lib
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(
    FILES ${BUTTERAUGLI_SRC_DIR}/butteraugli/butteraugli.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/butteraugli
)

if(BUTTERAUGLI_TOOL)
    find_package(JPEG REQUIRED)
    find_package(PNG REQUIRED)

    add_executable(butteraugli ${BUTTERAUGLI_SRC_DIR}/butteraugli/butteraugli_main.cc)
    target_link_libraries(butteraugli PRIVATE butteraugli_lib JPEG::JPEG PNG::PNG)
    target_compile_features(butteraugli PRIVATE cxx_std_11)

    install(TARGETS butteraugli DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()
