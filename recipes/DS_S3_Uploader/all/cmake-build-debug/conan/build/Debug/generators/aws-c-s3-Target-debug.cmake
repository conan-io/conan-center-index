# Avoid multiple calls to find_package to append duplicated properties to the targets
include_guard()########### VARIABLES #######################################################################
#############################################################################################
set(aws-c-s3_FRAMEWORKS_FOUND_DEBUG "") # Will be filled later
conan_find_apple_frameworks(aws-c-s3_FRAMEWORKS_FOUND_DEBUG "${aws-c-s3_FRAMEWORKS_DEBUG}" "${aws-c-s3_FRAMEWORK_DIRS_DEBUG}")

set(aws-c-s3_LIBRARIES_TARGETS "") # Will be filled later


######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
if(NOT TARGET aws-c-s3_DEPS_TARGET)
    add_library(aws-c-s3_DEPS_TARGET INTERFACE IMPORTED)
endif()

set_property(TARGET aws-c-s3_DEPS_TARGET
             APPEND PROPERTY INTERFACE_LINK_LIBRARIES
             $<$<CONFIG:Debug>:${aws-c-s3_FRAMEWORKS_FOUND_DEBUG}>
             $<$<CONFIG:Debug>:${aws-c-s3_SYSTEM_LIBS_DEBUG}>
             $<$<CONFIG:Debug>:AWS::aws-c-auth;AWS::aws-c-http;AWS::aws-c-io;AWS::aws-c-cal;AWS::aws-checksums;AWS::aws-c-common>)

####### Find the libraries declared in cpp_info.libs, create an IMPORTED target for each one and link the
####### aws-c-s3_DEPS_TARGET to all of them
conan_package_library_targets("${aws-c-s3_LIBS_DEBUG}"    # libraries
                              "${aws-c-s3_LIB_DIRS_DEBUG}" # package_libdir
                              "${aws-c-s3_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-c-s3_LIBRARY_TYPE_DEBUG}"
                              "${aws-c-s3_IS_HOST_WINDOWS_DEBUG}"
                              aws-c-s3_DEPS_TARGET
                              aws-c-s3_LIBRARIES_TARGETS  # out_libraries_targets
                              "_DEBUG"
                              "aws-c-s3"    # package_name
                              "${aws-c-s3_NO_SONAME_MODE_DEBUG}")  # soname

# FIXME: What is the result of this for multi-config? All configs adding themselves to path?
set(CMAKE_MODULE_PATH ${aws-c-s3_BUILD_DIRS_DEBUG} ${CMAKE_MODULE_PATH})

########## GLOBAL TARGET PROPERTIES Debug ########################################
    set_property(TARGET AWS::aws-c-s3
                 APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                 $<$<CONFIG:Debug>:${aws-c-s3_OBJECTS_DEBUG}>
                 $<$<CONFIG:Debug>:${aws-c-s3_LIBRARIES_TARGETS}>
                 )

    if("${aws-c-s3_LIBS_DEBUG}" STREQUAL "")
        # If the package is not declaring any "cpp_info.libs" the package deps, system libs,
        # frameworks etc are not linked to the imported targets and we need to do it to the
        # global target
        set_property(TARGET AWS::aws-c-s3
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     aws-c-s3_DEPS_TARGET)
    endif()

    set_property(TARGET AWS::aws-c-s3
                 APPEND PROPERTY INTERFACE_LINK_OPTIONS
                 $<$<CONFIG:Debug>:${aws-c-s3_LINKER_FLAGS_DEBUG}>)
    set_property(TARGET AWS::aws-c-s3
                 APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                 $<$<CONFIG:Debug>:${aws-c-s3_INCLUDE_DIRS_DEBUG}>)
    # Necessary to find LINK shared libraries in Linux
    set_property(TARGET AWS::aws-c-s3
                 APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                 $<$<CONFIG:Debug>:${aws-c-s3_LIB_DIRS_DEBUG}>)
    set_property(TARGET AWS::aws-c-s3
                 APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                 $<$<CONFIG:Debug>:${aws-c-s3_COMPILE_DEFINITIONS_DEBUG}>)
    set_property(TARGET AWS::aws-c-s3
                 APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                 $<$<CONFIG:Debug>:${aws-c-s3_COMPILE_OPTIONS_DEBUG}>)

########## For the modules (FindXXX)
set(aws-c-s3_LIBRARIES_DEBUG AWS::aws-c-s3)
