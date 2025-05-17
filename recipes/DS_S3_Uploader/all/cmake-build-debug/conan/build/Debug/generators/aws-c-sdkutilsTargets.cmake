# Load the debug and release variables
file(GLOB DATA_FILES "${CMAKE_CURRENT_LIST_DIR}/aws-c-sdkutils-*-data.cmake")

foreach(f ${DATA_FILES})
    include(${f})
endforeach()

# Create the targets for all the components
foreach(_COMPONENT ${aws-c-sdkutils_COMPONENT_NAMES} )
    if(NOT TARGET ${_COMPONENT})
        add_library(${_COMPONENT} INTERFACE IMPORTED)
        message(${aws-c-sdkutils_MESSAGE_MODE} "Conan: Component target declared '${_COMPONENT}'")
    endif()
endforeach()

if(NOT TARGET AWS::aws-c-sdkutils)
    add_library(AWS::aws-c-sdkutils INTERFACE IMPORTED)
    message(${aws-c-sdkutils_MESSAGE_MODE} "Conan: Target declared 'AWS::aws-c-sdkutils'")
endif()
# Load the debug and release library finders
file(GLOB CONFIG_FILES "${CMAKE_CURRENT_LIST_DIR}/aws-c-sdkutils-Target-*.cmake")

foreach(f ${CONFIG_FILES})
    include(${f})
endforeach()