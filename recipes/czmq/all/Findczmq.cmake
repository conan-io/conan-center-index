if(CONAN_INCLUDE_DIRS_CZMQ AND CONAN_LIBS_CZMQ)
	find_path(
        CZMQ_INCLUDE_DIRS 
        NAMES czmq.h 
        PATHS ${CONAN_INCLUDE_DIRS_CZMQ} 
        NO_CMAKE_FIND_ROOT_PATH
    )
    find_library(
        CZMQ_LIBRARIES 
        NAMES ${CONAN_LIBS_CZMQ} 
        PATHS ${CONAN_LIB_DIRS_CZMQ} 
        NO_CMAKE_FIND_ROOT_PATH
    )
else()
    if (NOT MSVC)
        include(FindPkgConfig)
        pkg_check_modules(PC_CZMQ "libczmq")
        if (PC_CZMQ_FOUND)
            # add CFLAGS from pkg-config file, e.g. draft api.
            add_definitions(${PC_CZMQ_CFLAGS} ${PC_CZMQ_CFLAGS_OTHER})
            # some libraries install the headers is a subdirectory of the include dir
            # returned by pkg-config, so use a wildcard match to improve chances of finding
            # headers and SOs.
            set(PC_CZMQ_INCLUDE_HINTS ${PC_CZMQ_INCLUDE_DIRS} ${PC_CZMQ_INCLUDE_DIRS}/*)
            set(PC_CZMQ_LIBRARY_HINTS ${PC_CZMQ_LIBRARY_DIRS} ${PC_CZMQ_LIBRARY_DIRS}/*)
        endif(PC_CZMQ_FOUND)
    endif (NOT MSVC)

    find_path (
        CZMQ_INCLUDE_DIRS
        NAMES czmq.h
        HINTS ${PC_CZMQ_INCLUDE_HINTS}
    )

    if (NOT CZMQ_LIBRARIES)
        find_library (
            CZMQ_LIBRARIES
            NAMES libczmq czmq
            HINTS ${PC_CZMQ_LIBRARY_HINTS}
        )
    endif ()
endif()

include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(
    CZMQ
    REQUIRED_VARS CZMQ_LIBRARIES CZMQ_INCLUDE_DIRS
)
mark_as_advanced(
    CZMQFOUND
    CZMQ_LIBRARIES CZMQ_INCLUDE_DIRS
)
