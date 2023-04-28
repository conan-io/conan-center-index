if(NOT TARGET CycloneDDS::idlc)
    if(CMAKE_CROSSCOMPILING)
        find_program(_idlc_executable
            NAMES idlc
            PATHS ENV PATH
            NO_DEFAULT_PATH
        )
    else()
        find_program(_idlc_executable
            NAMES idlc
            PATHS "${CMAKE_CURRENT_LIST_DIR}/../../../bin/"
            NO_DEFAULT_PATH
        )
    endif()
    # TODO: In conan v2 with CMakeToolchain, can be replaced by:
    # find_program(_idlc_executable NAMES idlc)
    # # Nice enough to handle CycloneDDS not in build_requires for native build
    # if(NOT _idlc_executable AND NOT CMAKE_CROSSCOMPILING)
    #     find_program(_idlc_executable
    #         NAMES idlc
    #         PATHS "${CMAKE_CURRENT_LIST_DIR}/../../bin/"
    #         NO_DEFAULT_PATH
    #     )
    # endif()

    if(_idlc_executable)
        get_filename_component(_idlc_executable "${_idlc_executable}" ABSOLUTE)
        add_executable(CycloneDDS::idlc IMPORTED)
        set_property(TARGET CycloneDDS::idlc PROPERTY IMPORTED_LOCATION ${_idlc_executable})
    endif()
endif()
