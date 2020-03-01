if(CONAN_INCLUDE_DIRS_ZYRE AND CONAN_LIBS_ZYRE)
	find_path(
        ZYRE_INCLUDE_DIRS 
        NAMES zyre.h zyre_library.h 
        PATHS ${CONAN_INCLUDE_DIRS_ZYRE} 
        NO_CMAKE_FIND_ROOT_PATH)
    find_library(
        ZYRE_LIBRARIES 
        NAMES ${CONAN_LIBS_ZYRE} 
        PATHS ${CONAN_LIB_DIRS_ZYRE} 
        NO_CMAKE_FIND_ROOT_PATH
    )
else()
    if (NOT MSVC)
        include(FindPkgConfig)
        pkg_check_modules(PC_ZYRE "zyre")
        if (PC_ZYRE_FOUND)
            # add CFLAGS from pkg-config file, e.g. draft api.
            add_definitions(${PC_ZYRE_CFLAGS} ${PC_ZYRE_CFLAGS_OTHER})
            # some libraries install the headers is a subdirectory of the include dir
            # returned by pkg-config, so use a wildcard match to improve chances of finding
            # headers and SOs.
            set(PC_ZYRE_INCLUDE_HINTS ${PC_ZYRE_INCLUDE_DIRS} ${PC_ZYRE_INCLUDE_DIRS}/*)
            set(PC_ZYRE_LIBRARY_HINTS ${PC_ZYRE_LIBRARY_DIRS} ${PC_ZYRE_LIBRARY_DIRS}/*)
        endif(PC_ZYRE_FOUND)
    endif (NOT MSVC)
        
    find_path (
        ZYRE_INCLUDE_DIRS
        NAMES zyre.h zyre_library.h
        HINTS ${PC_ZYRE_INCLUDE_HINTS}
    )

    if (NOT ZYRE_LIBRARIES)
            find_library (
                ZYRE_LIBRARIES
                NAMES libzyre zyre
                HINTS ${PC_ZYRE_LIBRARY_HINTS}
            )
    endif ()
endif()

include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(
    ZYRE
    REQUIRED_VARS ZYRE_LIBRARIES ZYRE_INCLUDE_DIRS
)
mark_as_advanced(
    ZYREFOUND
    ZYRE_LIBRARIES ZYRE_INCLUDE_DIRS
)
