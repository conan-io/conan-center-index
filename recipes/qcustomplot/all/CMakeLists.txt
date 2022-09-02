cmake_minimum_required(VERSION 3.8)
project(qcustomplot LANGUAGES CXX)

option(QCUSTOMPLOT_USE_OPENGL "Use OpenGL" OFF)

add_library(${PROJECT_NAME} ${QCUSTOMPLOT_SRC_DIR}/qcustomplot.cpp)
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        AUTOMOC ON
        DEBUG_POSTFIX "d"
        VERSION ${QCUSTOMPLOT_VERSION}
        SOVERSION ${QCUSTOMPLOT_VERSION_MAJOR}
)
if(BUILD_SHARED_LIBS)
    target_compile_definitions(${PROJECT_NAME}
        PRIVATE QCUSTOMPLOT_COMPILE_LIBRARY
        INTERFACE QCUSTOMPLOT_USE_LIBRARY
    )
    set_target_properties(${PROJECT_NAME}
        PROPERTIES
            CXX_VISIBILITY_PRESET hidden
            VISIBILITY_INLINES_HIDDEN ON
    )
endif()

if(QCUSTOMPLOT_USE_OPENGL)
    target_compile_definitions(${PROJECT_NAME} PUBLIC QCUSTOMPLOT_USE_OPENGL)

    # Set a variable to ensure that OpenGL is found through the find_package statements below.
    set(OPENGL_COMPONENT "OpenGL")

    # QCustomPlot does not use the QOpenGLFunctions class, and instead needs to link directly
    # to OpenGL32.lib on Windows, regardless of whether qt:opengl is 'dynamic' or 'desktop'
    if(WIN32)
        find_package(OpenGL REQUIRED)
        target_link_libraries(${PROJECT_NAME} PRIVATE OpenGL::GL)
    endif()
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

install(FILES ${QCUSTOMPLOT_SRC_DIR}/qcustomplot.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
