#Variable definition as proposed in
#https://cmake.org/cmake/help/book/mastering-cmake/chapter/Finding%20Packages.html#built-in-find-modules

set(Cantera_ROOT_DIR ${CMAKE_CURRENT_LIST_DIR})
mark_as_advanced(Cantera_ROOT_DIR)

# Look for the header file.
find_path(Cantera_INCLUDE_DIRS NAMES cantera/thermo.h)
mark_as_advanced(Cantera_INCLUDE_DIRS)

# Look for the library
find_library(Cantera_LIBRARIES NAMES
        cantera_shared
        HINTS "${CMAKE_CURRENT_LIST_DIR}/bin"
    )
mark_as_advanced(Cantera_LIBRARIES)

# Look for the shared library
# Since Cantera is a library and not a executable, this contains the shared labrary files (so and dll)
find_file(Cantera_EXECUTABLE NAMES
        cantera_shared.dll
		libcantera_shared.so.3
        HINTS "${CMAKE_CURRENT_LIST_DIR}/bin" "${CMAKE_CURRENT_LIST_DIR}/lib"
    )
mark_as_advanced(Cantera_EXECUTABLE)

# Look vor version number
if(Cantera_INCLUDE_DIRS)
    set(CANTERA_VERSION_FILE "${Cantera_INCLUDE_DIRS}/cantera/base/config.h")
    if(EXISTS "${CANTERA_VERSION_FILE}")
        file(STRINGS "${CANTERA_VERSION_FILE}" cantera_version_str REGEX "^#define[\r\n\t ]+CANTERA_VERSION[\r\n\t ]+\".*\"")
        string(REGEX REPLACE "^#define[\r\n\t ]+CANTERA_VERSION[\r\n\t ]+\"([^\"]*)\".*" "\\1" Cantera_VERSION "${cantera_version_str}")
        unset(cantera_version_str)
    endif()
endif()

set(Cantera_VERSION_${Cantera_VERSION} TRUE)
mark_as_advanced(Cantera_VERSION_${Cantera_VERSION})

# handle the QUIETLY and REQUIRED arguments and set CANTERA_FOUND to TRUE if
# all listed variables are TRUE
include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(Cantera
                                  REQUIRED_VARS Cantera_LIBRARIES Cantera_INCLUDE_DIRS
                                  VERSION_VAR Cantera_VERSION
    )

if(Cantera_FOUND)
    add_library(Cantera::cantera SHARED IMPORTED)
    set_target_properties(Cantera::cantera PROPERTIES
          INTERFACE_INCLUDE_DIRECTORIES ${Cantera_INCLUDE_DIRS}
          IMPORTED_LOCATION ${Cantera_EXECUTABLE}
          IMPORTED_IMPLIB ${Cantera_LIBRARIES}
      )
endif(Cantera_FOUND)
