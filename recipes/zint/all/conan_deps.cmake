if(ZINT_USE_QT)
    message(STATUS "Using Qt${QT_VERSION_MAJOR}")
    find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Gui)
endif()
