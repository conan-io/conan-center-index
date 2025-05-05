cmake_minimum_required(VERSION 3.1)
project(libstudxml LANGUAGES C CXX)

find_package(EXPAT REQUIRED MODULE)

add_library(studxml
    ${LIBSTUDXML_SRC_DIR}/libstudxml/parser.cxx
    ${LIBSTUDXML_SRC_DIR}/libstudxml/qname.cxx
    ${LIBSTUDXML_SRC_DIR}/libstudxml/serializer.cxx
    ${LIBSTUDXML_SRC_DIR}/libstudxml/value-traits.cxx
    ${LIBSTUDXML_SRC_DIR}/libstudxml/details/genx/char-props.c
    ${LIBSTUDXML_SRC_DIR}/libstudxml/details/genx/genx.c
)
target_include_directories(studxml PUBLIC ${LIBSTUDXML_SRC_DIR})
target_link_libraries(studxml PUBLIC EXPAT::EXPAT)

if(BUILD_SHARED_LIBS)
    target_compile_definitions(studxml
        PRIVATE LIBSTUDXML_SHARED_BUILD
        INTERFACE LIBSTUDXML_SHARED
    )
else()
    target_compile_definitions(studxml
        PRIVATE LIBSTUDXML_STATIC_BUILD
        INTERFACE LIBSTUDXML_STATIC
    )
endif()

include(GNUInstallDirs)
install(
    TARGETS studxml
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(
    DIRECTORY ${LIBSTUDXML_SRC_DIR}/libstudxml
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING REGEX "(.*).(h|hxx|ixx|txx)$"
)
