cmake_minimum_required(VERSION 3.8)
project(arsenalgear LANGUAGES CXX)

include(GNUInstallDirs)

add_library(arsenalgear ${arsenalgear_src})
target_sources(arsenalgear PRIVATE
    $<$<VERSION_LESS_EQUAL:${ARSENALGEAR_VERSION},1.2.2>:
        ${ARSENALGEAR_SRC_DIR}/src/operators.cpp
    >
    ${ARSENALGEAR_SRC_DIR}/src/stream.cpp
    ${ARSENALGEAR_SRC_DIR}/src/system.cpp
    ${ARSENALGEAR_SRC_DIR}/src/utils.cpp
)
target_include_directories(arsenalgear PRIVATE "${ARSENALGEAR_SRC_DIR}/include")
set_target_properties(arsenalgear PROPERTIES
    PUBLIC_HEADER "${arsenalgear_inc}"
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)
target_compile_features(arsenalgear PUBLIC cxx_std_17)

if(${ARSENALGEAR_VERSION} VERSION_LESS 2.0.0)
    find_package(Boost REQUIRED CONFIG)
    target_link_libraries(arsenalgear PUBLIC Boost::headers)

    find_package(exprtk CONFIG)
    if(${exprtk_FOUND})
        target_link_libraries(arsenalgear PUBLIC exprtk::exprtk)
    endif()
endif()

find_library(LIBM m)
target_link_libraries(arsenalgear PRIVATE $<$<BOOL:${LIBM}>:${LIBM}>)

install(
    TARGETS arsenalgear
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(
    DIRECTORY ${ARSENALGEAR_SRC_DIR}/include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/arsenalgear
)
