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

    if(_idlc_executable)
        get_filename_component(_idlc_executable "${_idlc_executable}" ABSOLUTE)
        add_executable(CycloneDDS::idlc IMPORTED)
        set_property(TARGET CycloneDDS::idlc PROPERTY IMPORTED_LOCATION ${_idlc_executable})
    endif()
endif()

# Define CycloneDDS::libidlc so IDLC_GENERATE uses $<TARGET_FILE:CycloneDDS::libidlc>
# rather than falling back to find_library(), which on Windows returns the import .lib
# instead of the .dll, causing LoadLibrary to fail at code-generation time.
if(NOT TARGET CycloneDDS::libidlc AND NOT CMAKE_CROSSCOMPILING)
    if(WIN32)
        find_file(_libidlc_location
            NAMES cycloneddsidlc.dll
            PATHS "${CMAKE_CURRENT_LIST_DIR}/../../../bin/"
            NO_DEFAULT_PATH
        )
    else()
        find_library(_libidlc_location
            NAMES cycloneddsidlc
            PATHS "${CMAKE_CURRENT_LIST_DIR}/../../../lib/"
            NO_DEFAULT_PATH
        )
    endif()

    if(_libidlc_location)
        get_filename_component(_libidlc_location "${_libidlc_location}" ABSOLUTE)
        add_library(CycloneDDS::libidlc SHARED IMPORTED)
        set_property(TARGET CycloneDDS::libidlc PROPERTY IMPORTED_LOCATION ${_libidlc_location})
    endif()
endif()
