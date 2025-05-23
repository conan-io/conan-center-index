########## MACROS ###########################################################################
#############################################################################################

# Requires CMake > 3.15
if(${CMAKE_VERSION} VERSION_LESS "3.15")
    message(FATAL_ERROR "The 'CMakeDeps' generator only works with CMake >= 3.15")
endif()

if(AWSSDK_FIND_QUIETLY)
    set(AWSSDK_MESSAGE_MODE VERBOSE)
else()
    set(AWSSDK_MESSAGE_MODE STATUS)
endif()

include(${CMAKE_CURRENT_LIST_DIR}/cmakedeps_macros.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/AWSSDKTargets.cmake)
include(CMakeFindDependencyMacro)

check_build_type_defined()

foreach(_DEPENDENCY ${aws-sdk-cpp_FIND_DEPENDENCY_NAMES} )
    # Check that we have not already called a find_package with the transitive dependency
    if(NOT ${_DEPENDENCY}_FOUND)
        find_dependency(${_DEPENDENCY} REQUIRED ${${_DEPENDENCY}_FIND_MODE})
    endif()
endforeach()

set(AWSSDK_VERSION_STRING "1.11.352")
set(AWSSDK_INCLUDE_DIRS ${aws-sdk-cpp_INCLUDE_DIRS_DEBUG} )
set(AWSSDK_INCLUDE_DIR ${aws-sdk-cpp_INCLUDE_DIRS_DEBUG} )
set(AWSSDK_LIBRARIES ${aws-sdk-cpp_LIBRARIES_DEBUG} )
set(AWSSDK_DEFINITIONS ${aws-sdk-cpp_DEFINITIONS_DEBUG} )


# Only the last installed configuration BUILD_MODULES are included to avoid the collision
foreach(_BUILD_MODULE ${aws-sdk-cpp_BUILD_MODULES_PATHS_DEBUG} )
    message(${AWSSDK_MESSAGE_MODE} "Conan: Including build module from '${_BUILD_MODULE}'")
    include(${_BUILD_MODULE})
endforeach()


