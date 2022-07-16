cmake_minimum_required(VERSION 3.8)
project(qcustomplot CXX)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS KEEP_RPATHS)

add_library(${PROJECT_NAME} source_subfolder/qcustomplot.cpp)
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        AUTOMOC ON
        DEBUG_POSTFIX "d"
        VERSION ${CONAN_PACKAGE_VERSION}
)
if(BUILD_SHARED_LIBS)
    # get major version via 'conanbuildinfo.cmake'
    string(REPLACE "." ";" VERSION_LIST ${CONAN_PACKAGE_VERSION})
    list(GET VERSION_LIST 0 CONAN_PACKAGE_VERSION_MAJOR)

    target_compile_definitions(${PROJECT_NAME}
        PRIVATE QCUSTOMPLOT_COMPILE_LIBRARY
        INTERFACE QCUSTOMPLOT_USE_LIBRARY
    )
    set_target_properties(${PROJECT_NAME}
        PROPERTIES
            CXX_VISIBILITY_PRESET hidden
            VISIBILITY_INLINES_HIDDEN ON
            SOVERSION ${CONAN_PACKAGE_VERSION_MAJOR}
    )
endif()

option(QCUSTOMPLOT_USE_OPENGL "Use OpenGL" OFF)

if(QCUSTOMPLOT_USE_OPENGL)
    target_compile_definitions(${PROJECT_NAME} PUBLIC QCUSTOMPLOT_USE_OPENGL)

    #Set a variable to ensure that OpenGL is found through the find_package statements below.
    set(OPENGL_COMPONENT "OpenGL")

    #QCustomPlot does not use the QOpenGLFunctions class, and instead needs to link directly
    #to OpenGL32.lib on Windows, regardless of whether qt:opengl is 'dynamic' or 'desktop'
    if (MSVC)
        target_link_libraries(${PROJECT_NAME} PRIVATE OpenGL32)
    endif()

    #QtX::OpenGL is added as a link library using generator expression below.
endif()

if(QT_VERSION VERSION_GREATER_EQUAL "6.0.0")
    find_package(Qt6 COMPONENTS Core Gui Widgets PrintSupport ${OPENGL_COMPONENT} REQUIRED CONFIG)
    target_link_libraries(${PROJECT_NAME} PUBLIC Qt6::Core Qt6::Gui Qt6::Widgets Qt6::PrintSupport 
                                                 $<$<BOOL:${QCUSTOMPLOT_USE_OPENGL}>:Qt6::OpenGL>)
    target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_17)
elseif(QT_VERSION VERSION_GREATER_EQUAL "5.0.0")
    find_package(Qt5 COMPONENTS Core Gui Widgets PrintSupport ${OPENGL_COMPONENT} REQUIRED CONFIG)
    target_link_libraries(${PROJECT_NAME} PUBLIC Qt5::Core Qt5::Gui Qt5::Widgets Qt5::PrintSupport
                                                 $<$<BOOL:${QCUSTOMPLOT_USE_OPENGL}>:Qt5::OpenGL>)
    target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_11)
else()
    message(FATAL_ERROR "Qt < 5 not yet supported in this recipe")
endif()

install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(FILES source_subfolder/qcustomplot.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
