find_path(DAG_INCLUDE_PATH NAMES dagapi.h)
find_library(DAG_LIBRARY NAMES dag)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(DAG
    REQUIRED_VARS DAG_LIBRARY DAG_INCLUDE_PATH
)

if(DAG_FOUND AND NOT TARGET DAG::DAG)
    add_library(DAG::DAG UNKNOWN IMPORTED)
    set_target_properties(DAG::DAG
        PROPERTIES
            IMPORTED_LOCATION "${DAG_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES"${DAG_INCLUDE_PATH}"
    )
endif()
