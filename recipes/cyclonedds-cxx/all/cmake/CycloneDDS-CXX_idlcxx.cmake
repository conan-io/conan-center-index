if(NOT TARGET CycloneDDS-CXX::idlcxx)
    if(CMAKE_CROSSCOMPILING)
        find_library(_idlcxx_shared_lib
            NAMES cycloneddsidlcxx
            PATHS ENV PATH ENV LD_LIBRARY_PATH
            NO_DEFAULT_PATH
        )
    else()
        find_library(_idlcxx_shared_lib
            NAMES cycloneddsidlcxx
            PATHS "${CMAKE_CURRENT_LIST_DIR}/../../../lib/"
            NO_DEFAULT_PATH
        )
    endif()

    if(NOT ("${_idlcxx_shared_lib}" EQUAL "_idlcxx_shared_lib-NOTFOUND"))
        get_filename_component(_idlc_shared_lib "${_idlcxx_shared_lib}" ABSOLUTE)
        add_library(CycloneDDS-CXX::idlcxx IMPORTED SHARED)
        set_property(TARGET CycloneDDS-CXX::idlcxx PROPERTY IMPORTED_LOCATION ${_idlcxx_shared_lib})
    else()
        message(FATAL_ERROR "Unable to find cycloneddsidlcxx shared library!")
    endif()
endif()
