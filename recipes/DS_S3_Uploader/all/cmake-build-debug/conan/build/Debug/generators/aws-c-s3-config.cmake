########## MACROS ###########################################################################
#############################################################################################

# Requires CMake > 3.15
if(${CMAKE_VERSION} VERSION_LESS "3.15")
    message(FATAL_ERROR "The 'CMakeDeps' generator only works with CMake >= 3.15")
endif()

if(aws-c-s3_FIND_QUIETLY)
    set(aws-c-s3_MESSAGE_MODE VERBOSE)
else()
    set(aws-c-s3_MESSAGE_MODE STATUS)
endif()

include(${CMAKE_CURRENT_LIST_DIR}/cmakedeps_macros.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/aws-c-s3Targets.cmake)
include(CMakeFindDependencyMacro)

check_build_type_defined()

foreach(_DEPENDENCY ${aws-c-s3_FIND_DEPENDENCY_NAMES} )
    # Check that we have not already called a find_package with the transitive dependency
    if(NOT ${_DEPENDENCY}_FOUND)
        find_dependency(${_DEPENDENCY} REQUIRED ${${_DEPENDENCY}_FIND_MODE})
    endif()
endforeach()

set(aws-c-s3_VERSION_STRING "0.5.5")
set(aws-c-s3_INCLUDE_DIRS ${aws-c-s3_INCLUDE_DIRS_DEBUG} )
set(aws-c-s3_INCLUDE_DIR ${aws-c-s3_INCLUDE_DIRS_DEBUG} )
set(aws-c-s3_LIBRARIES ${aws-c-s3_LIBRARIES_DEBUG} )
set(aws-c-s3_DEFINITIONS ${aws-c-s3_DEFINITIONS_DEBUG} )


# Only the last installed configuration BUILD_MODULES are included to avoid the collision
foreach(_BUILD_MODULE ${aws-c-s3_BUILD_MODULES_PATHS_DEBUG} )
    message(${aws-c-s3_MESSAGE_MODE} "Conan: Including build module from '${_BUILD_MODULE}'")
    include(${_BUILD_MODULE})
endforeach()


