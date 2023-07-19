

function(add_qt_executable target)
    add_executable( ${target} WIN32 ${ARGN} )

    target_compile_features( ${target} PRIVATE cxx_std_11 )
    set_target_properties( ${target} PROPERTIES AUTOMOC ON AUTORCC ON )
endfunction()

function(link_to_platforms_plugin_if_qt_is_static target lib test_exe_opts)

    if(TEST_PACKAGE_QT_SHARED_LIBS)
        return()
    endif()

    set(dependencies ${qt_Qt5_${lib}_DEPENDENCIES_RELEASE})
    if(NOT (Qt5::Gui IN_LIST dependencies) AND
       NOT (lib STREQUAL Gui))
        return()
    endif()


    target_compile_definitions( ${target} PRIVATE
        TEST_PACKAGE_USE_QT_STATIC
    )
    target_link_libraries( ${target} PRIVATE Qt5::QMinimalIntegrationPlugin)
    set(${test_exe_opts} -platform minimal PARENT_SCOPE)


endfunction()

macro(add_qt_exe lib )
    set(target ${PROJECT_NAME}-${lib})
    
    add_qt_executable( ${target} test_package-${lib}.cpp ${ARGN} )

    find_package(Qt5 COMPONENTS ${lib} REQUIRED CONFIG)
    target_link_libraries( ${target} PRIVATE Qt5::${lib})

    link_to_platforms_plugin_if_qt_is_static(${target} ${lib} EXE_OPTS)

    add_test( NAME ${target} COMMAND ${target} ${EXE_OPTS})
    
endmacro()

include(CTest)


list(REMOVE_ITEM QT_MODULE Core)
add_qt_exe( Core greeter.h example.qrc )

foreach(lib IN LISTS QT_MODULE)
    add_qt_exe( ${lib} )
endforeach()

