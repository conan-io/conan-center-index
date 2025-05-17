# Load the debug and release variables
file(GLOB DATA_FILES "${CMAKE_CURRENT_LIST_DIR}/aws-checksums-*-data.cmake")

foreach(f ${DATA_FILES})
    include(${f})
endforeach()

# Create the targets for all the components
foreach(_COMPONENT ${aws-checksums_COMPONENT_NAMES} )
    if(NOT TARGET ${_COMPONENT})
        add_library(${_COMPONENT} INTERFACE IMPORTED)
        message(${aws-checksums_MESSAGE_MODE} "Conan: Component target declared '${_COMPONENT}'")
    endif()
endforeach()

if(NOT TARGET AWS::aws-checksums)
    add_library(AWS::aws-checksums INTERFACE IMPORTED)
    message(${aws-checksums_MESSAGE_MODE} "Conan: Target declared 'AWS::aws-checksums'")
endif()
# Load the debug and release library finders
file(GLOB CONFIG_FILES "${CMAKE_CURRENT_LIST_DIR}/aws-checksums-Target-*.cmake")

foreach(f ${CONFIG_FILES})
    include(${f})
endforeach()