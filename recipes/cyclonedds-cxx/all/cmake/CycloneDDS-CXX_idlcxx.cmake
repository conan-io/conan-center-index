if(NOT TARGET CycloneDDS-CXX::idlcxx)
    set(_OLD_CMAKE_FIND_LIBRARY_SUFFIXES ${CMAKE_FIND_LIBRARY_SUFFIXES})
    set(CMAKE_FIND_LIBRARY_SUFFIXES .dll .dll.a ${CMAKE_FIND_LIBRARY_SUFFIXES})
    if(CMAKE_CROSSCOMPILING)
        find_library(_idlcxx_shared_lib
            NAMES cycloneddsidlcxx
            PATHS ENV PATH ENV LD_LIBRARY_PATH
            NO_DEFAULT_PATH
        )
    else()
        find_library(_idlcxx_shared_lib
            NAMES cycloneddsidlcxx
            PATHS "${CMAKE_CURRENT_LIST_DIR}/../../../bin/"
                  "${CMAKE_CURRENT_LIST_DIR}/../../../lib/"
            NO_DEFAULT_PATH
        )
    endif()

    set(CMAKE_FIND_LIBRARY_SUFFIXES ${_OLD_CMAKE_FIND_LIBRARY_SUFFIXES})
    if(NOT ("${_idlcxx_shared_lib}" EQUAL "_idlcxx_shared_lib-NOTFOUND"))
        get_filename_component(_idlc_shared_lib "${_idlcxx_shared_lib}" ABSOLUTE)
        add_library(CycloneDDS-CXX::idlcxx IMPORTED SHARED)
        set_property(TARGET CycloneDDS-CXX::idlcxx PROPERTY IMPORTED_LOCATION ${_idlcxx_shared_lib})
        message(STATUS "CycloneDDS-CXX::idlcxx IMPORTED_LOCATION = ${_idlcxx_shared_lib}")

        if(WIN32)
            if(CMAKE_CROSSCOMPILING)
                find_library(_idlcxx_imp_lib
                    NAMES cycloneddsidlcxx
                    PATHS ENV PATH ENV LD_LIBRARY_PATH
                    NO_DEFAULT_PATH
                )
            else()
                find_library(_idlcxx_imp_lib
                    NAMES cycloneddsidlcxx
                    PATHS "${CMAKE_CURRENT_LIST_DIR}/../../../lib/"
                    NO_DEFAULT_PATH
                )
            endif()
            set_property(TARGET CycloneDDS-CXX::idlcxx PROPERTY IMPORTED_IMPLIB ${_idlcxx_imp_lib})
            message(STATUS "CycloneDDS-CXX::idlcxx IMPORTED_IMPLIB = ${_idlcxx_imp_lib}")
        endif()

    endif()
endif()
