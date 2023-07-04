

macro(link_static_plateform_integration_plugin_if_needed target)
endmacro()


macro(add_qt_exe lib )
    
    find_package(Qt5 COMPONENTS ${lib} REQUIRED CONFIG)

    set(target ${PROJECT_NAME}-${lib})
    
    add_executable( ${target} WIN32 test_package-${lib}.cpp ${ARGN} )
    target_link_libraries( ${target} PRIVATE Qt5::${lib})
    target_compile_features( ${target} PRIVATE cxx_std_11 )
    set_target_properties( ${target} PROPERTIES AUTOMOC ON AUTORCC ON )

    set(dependencies ${qt_Qt5_${lib}_DEPENDENCIES_RELEASE})
    if(NOT TEST_PACKAGE_QT_SHARED_LIBS)
        if((Qt5::Gui IN_LIST dependencies) OR (lib STREQUAL Gui))
            target_compile_definitions( ${target} PRIVATE
                TEST_PACKAGE_USE_QT_STATIC
            )
            target_link_libraries( ${target} PRIVATE Qt5::QMinimalIntegrationPlugin)
            set(EXE_OPTS -platform minimal)
        endif()
    endif()
        
    
    add_test( NAME ${target} COMMAND ${PROJECT_NAME}-${lib} ${EXE_OPTS})
    
endmacro()

include(CTest)


list(REMOVE_ITEM QT_MODULE Core)
add_qt_exe( Core greeter.h example.qrc )

foreach(lib IN LISTS QT_MODULE)
    add_qt_exe( ${lib} )
endforeach()

