find_path(TURBOCAP_INCLUDE_PATH NAMES TcApi.h)
find_library(TURBOCAP_LIBRARY NAMES TcApi)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Turbocap
    REQUIRED_VARS TURBOCAP_LIBRARY TURBOCAP_INCLUDE_PATH
)

if(DAG_FOUND AND NOT TARGET Turbocap::Turbocap)
    add_library(Turbocap::Turbocap UNKNOWN IMPORTED)
    set_target_properties(Turbocap::Turbocap
        PROPERTIES
            IMPORTED_LOCATION "${TURBOCAP_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES"${TURBOCAP_INCLUDE_PATH}"
    )
endif()
