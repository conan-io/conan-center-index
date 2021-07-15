find_path(SEPTEL_INCLUDE_PATH NAMES msg.h)
find_library(SEPTEL_LIBRARY NAMES septel)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(septel
    REQUIRED_VARS SEPTEL_LIBRARY SEPTEL_INCLUDE_PATH
)

if(septel_FOUND AND NOT TARGET septel::septel)
    add_library(septel::septel UNKNOWN IMPORTED)
    set_target_properties(septel::septel
        PROPERTIES
            IMPORTED_LOCATION "${SEPTEL_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES"${SEPTEL_INCLUDE_PATH}"
    )
endif()
