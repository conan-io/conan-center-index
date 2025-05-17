# Avoid multiple calls to find_package to append duplicated properties to the targets
include_guard()########### VARIABLES #######################################################################
#############################################################################################
set(aws-sdk-cpp_FRAMEWORKS_FOUND_DEBUG "") # Will be filled later
conan_find_apple_frameworks(aws-sdk-cpp_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_FRAMEWORK_DIRS_DEBUG}")

set(aws-sdk-cpp_LIBRARIES_TARGETS "") # Will be filled later


######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
if(NOT TARGET aws-sdk-cpp_DEPS_TARGET)
    add_library(aws-sdk-cpp_DEPS_TARGET INTERFACE IMPORTED)
endif()

set_property(TARGET aws-sdk-cpp_DEPS_TARGET
             APPEND PROPERTY INTERFACE_LINK_LIBRARIES
             $<$<CONFIG:Debug>:${aws-sdk-cpp_FRAMEWORKS_FOUND_DEBUG}>
             $<$<CONFIG:Debug>:${aws-sdk-cpp_SYSTEM_LIBS_DEBUG}>
             $<$<CONFIG:Debug>:AWS::aws-crt-cpp;AWS::aws-c-auth;AWS::aws-c-cal;AWS::aws-c-common;AWS::aws-c-compression;AWS::aws-c-event-stream;AWS::aws-c-http;AWS::aws-c-io;AWS::aws-c-mqtt;AWS::aws-checksums;ZLIB::ZLIB;AWS::aws-c-sdkutils;AWS::aws-sdk-cpp-core;AWS::aws-sdk-cpp-iam;AWS::aws-sdk-cpp-cognito-identity;AWS::aws-sdk-cpp-access-management;AWS::aws-sdk-cpp-sts;AWS::aws-sdk-cpp-identity-management;AWS::aws-sdk-cpp-kms;AWS::aws-sdk-cpp-monitoring;AWS::aws-sdk-cpp-polly;AWS::aws-sdk-cpp-sqs;AWS::aws-sdk-cpp-queues;AWS::aws-sdk-cpp-s3;AWS::aws-sdk-cpp-s3-encryption;AWS::aws-sdk-cpp-text-to-speech;AWS::aws-sdk-cpp-transfer>)

####### Find the libraries declared in cpp_info.libs, create an IMPORTED target for each one and link the
####### aws-sdk-cpp_DEPS_TARGET to all of them
conan_package_library_targets("${aws-sdk-cpp_LIBS_DEBUG}"    # libraries
                              "${aws-sdk-cpp_LIB_DIRS_DEBUG}" # package_libdir
                              "${aws-sdk-cpp_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_DEPS_TARGET
                              aws-sdk-cpp_LIBRARIES_TARGETS  # out_libraries_targets
                              "_DEBUG"
                              "aws-sdk-cpp"    # package_name
                              "${aws-sdk-cpp_NO_SONAME_MODE_DEBUG}")  # soname

# FIXME: What is the result of this for multi-config? All configs adding themselves to path?
set(CMAKE_MODULE_PATH ${aws-sdk-cpp_BUILD_DIRS_DEBUG} ${CMAKE_MODULE_PATH})

########## COMPONENTS TARGET PROPERTIES Debug ########################################

    ########## COMPONENT aws-sdk-cpp::aws-sdk-cpp-transfer_alias #############

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_DEPS_TARGET)
            add_library(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_LIBS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_DEPS_TARGET
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-transfer_alias
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-transfer_alias
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_DEPS_TARGET)
        endif()

        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-transfer_alias APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-transfer_alias APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-transfer_alias APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_LIB_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-transfer_alias APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-transfer_alias APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT aws-sdk-cpp::aws-sdk-cpp-text-to-speech_alias #############

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_DEPS_TARGET)
            add_library(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_LIBS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_DEPS_TARGET
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-text-to-speech_alias
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-text-to-speech_alias
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_DEPS_TARGET)
        endif()

        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-text-to-speech_alias APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-text-to-speech_alias APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-text-to-speech_alias APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_LIB_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-text-to-speech_alias APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-text-to-speech_alias APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT aws-sdk-cpp::aws-sdk-cpp-s3-encryption_alias #############

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_DEPS_TARGET)
            add_library(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_LIBS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_DEPS_TARGET
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-s3-encryption_alias
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-s3-encryption_alias
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_DEPS_TARGET)
        endif()

        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-s3-encryption_alias APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-s3-encryption_alias APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-s3-encryption_alias APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_LIB_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-s3-encryption_alias APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-s3-encryption_alias APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT aws-sdk-cpp::aws-sdk-cpp-queues_alias #############

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_DEPS_TARGET)
            add_library(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_LIBS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_DEPS_TARGET
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-queues_alias
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-queues_alias
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_DEPS_TARGET)
        endif()

        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-queues_alias APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-queues_alias APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-queues_alias APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_LIB_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-queues_alias APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-queues_alias APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT aws-sdk-cpp::aws-sdk-cpp-identity-management_alias #############

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_DEPS_TARGET)
            add_library(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_LIBS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_DEPS_TARGET
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-identity-management_alias
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-identity-management_alias
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_DEPS_TARGET)
        endif()

        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-identity-management_alias APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-identity-management_alias APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-identity-management_alias APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_LIB_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-identity-management_alias APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-identity-management_alias APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT aws-sdk-cpp::aws-sdk-cpp-access-management_alias #############

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_DEPS_TARGET)
            add_library(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_LIBS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_DEPS_TARGET
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-access-management_alias
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-access-management_alias
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_DEPS_TARGET)
        endif()

        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-access-management_alias APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-access-management_alias APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-access-management_alias APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_LIB_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-access-management_alias APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-access-management_alias APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT AWS::aws-sdk-cpp-transfer #############

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_DEPS_TARGET)
            add_library(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_LIBS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_DEPS_TARGET
                              aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_AWS_aws-sdk-cpp-transfer"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET AWS::aws-sdk-cpp-transfer
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET AWS::aws-sdk-cpp-transfer
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_DEPS_TARGET)
        endif()

        set_property(TARGET AWS::aws-sdk-cpp-transfer APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-transfer APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-transfer APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_LIB_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-transfer APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-transfer APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT AWS::aws-sdk-cpp-text-to-speech #############

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_DEPS_TARGET)
            add_library(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_LIBS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_DEPS_TARGET
                              aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET AWS::aws-sdk-cpp-text-to-speech
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET AWS::aws-sdk-cpp-text-to-speech
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_DEPS_TARGET)
        endif()

        set_property(TARGET AWS::aws-sdk-cpp-text-to-speech APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-text-to-speech APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-text-to-speech APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_LIB_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-text-to-speech APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-text-to-speech APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT aws-sdk-cpp::aws-sdk-cpp-sts_alias #############

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_DEPS_TARGET)
            add_library(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_LIBS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_DEPS_TARGET
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-sts_alias
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-sts_alias
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_DEPS_TARGET)
        endif()

        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-sts_alias APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-sts_alias APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-sts_alias APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_LIB_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-sts_alias APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-sts_alias APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT aws-sdk-cpp::aws-sdk-cpp-sqs_alias #############

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_DEPS_TARGET)
            add_library(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_LIBS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_DEPS_TARGET
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-sqs_alias
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-sqs_alias
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_DEPS_TARGET)
        endif()

        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-sqs_alias APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-sqs_alias APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-sqs_alias APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_LIB_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-sqs_alias APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-sqs_alias APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT AWS::aws-sdk-cpp-s3-encryption #############

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_DEPS_TARGET)
            add_library(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_LIBS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_DEPS_TARGET
                              aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET AWS::aws-sdk-cpp-s3-encryption
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET AWS::aws-sdk-cpp-s3-encryption
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_DEPS_TARGET)
        endif()

        set_property(TARGET AWS::aws-sdk-cpp-s3-encryption APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-s3-encryption APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-s3-encryption APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_LIB_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-s3-encryption APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-s3-encryption APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT aws-sdk-cpp::aws-sdk-cpp-s3_alias #############

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_DEPS_TARGET)
            add_library(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_LIBS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_DEPS_TARGET
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-s3_alias
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-s3_alias
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_DEPS_TARGET)
        endif()

        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-s3_alias APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-s3_alias APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-s3_alias APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_LIB_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-s3_alias APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-s3_alias APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT AWS::aws-sdk-cpp-queues #############

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-queues_DEPS_TARGET)
            add_library(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-queues_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_AWS_aws-sdk-cpp-queues_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_LIBS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_AWS_aws-sdk-cpp-queues_DEPS_TARGET
                              aws-sdk-cpp_AWS_aws-sdk-cpp-queues_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_AWS_aws-sdk-cpp-queues"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET AWS::aws-sdk-cpp-queues
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET AWS::aws-sdk-cpp-queues
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_AWS_aws-sdk-cpp-queues_DEPS_TARGET)
        endif()

        set_property(TARGET AWS::aws-sdk-cpp-queues APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-queues APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-queues APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_LIB_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-queues APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-queues APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT aws-sdk-cpp::aws-sdk-cpp-polly_alias #############

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_DEPS_TARGET)
            add_library(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_LIBS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_DEPS_TARGET
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-polly_alias
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-polly_alias
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_DEPS_TARGET)
        endif()

        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-polly_alias APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-polly_alias APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-polly_alias APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_LIB_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-polly_alias APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-polly_alias APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT aws-sdk-cpp::aws-sdk-cpp-monitoring_alias #############

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_DEPS_TARGET)
            add_library(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_LIBS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_DEPS_TARGET
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-monitoring_alias
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-monitoring_alias
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_DEPS_TARGET)
        endif()

        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-monitoring_alias APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-monitoring_alias APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-monitoring_alias APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_LIB_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-monitoring_alias APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-monitoring_alias APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT aws-sdk-cpp::aws-sdk-cpp-kms_alias #############

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_DEPS_TARGET)
            add_library(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_LIBS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_DEPS_TARGET
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-kms_alias
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-kms_alias
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_DEPS_TARGET)
        endif()

        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-kms_alias APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-kms_alias APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-kms_alias APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_LIB_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-kms_alias APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-kms_alias APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT AWS::aws-sdk-cpp-identity-management #############

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_DEPS_TARGET)
            add_library(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_LIBS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_DEPS_TARGET
                              aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET AWS::aws-sdk-cpp-identity-management
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET AWS::aws-sdk-cpp-identity-management
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_DEPS_TARGET)
        endif()

        set_property(TARGET AWS::aws-sdk-cpp-identity-management APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-identity-management APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-identity-management APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_LIB_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-identity-management APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-identity-management APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT aws-sdk-cpp::aws-sdk-cpp-iam_alias #############

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_DEPS_TARGET)
            add_library(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_LIBS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_DEPS_TARGET
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-iam_alias
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-iam_alias
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_DEPS_TARGET)
        endif()

        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-iam_alias APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-iam_alias APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-iam_alias APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_LIB_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-iam_alias APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-iam_alias APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT aws-sdk-cpp::aws-sdk-cpp-cognito-identity_alias #############

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_DEPS_TARGET)
            add_library(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_LIBS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_DEPS_TARGET
                              aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias"
                              "${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-cognito-identity_alias
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-cognito-identity_alias
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_DEPS_TARGET)
        endif()

        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-cognito-identity_alias APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-cognito-identity_alias APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-cognito-identity_alias APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_LIB_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-cognito-identity_alias APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::aws-sdk-cpp-cognito-identity_alias APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT AWS::aws-sdk-cpp-access-management #############

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_DEPS_TARGET)
            add_library(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_LIBS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_DEPS_TARGET
                              aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_AWS_aws-sdk-cpp-access-management"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET AWS::aws-sdk-cpp-access-management
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET AWS::aws-sdk-cpp-access-management
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_DEPS_TARGET)
        endif()

        set_property(TARGET AWS::aws-sdk-cpp-access-management APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-access-management APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-access-management APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_LIB_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-access-management APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-access-management APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT aws-sdk-cpp::plugin_scripts #############

        set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_DEPS_TARGET)
            add_library(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_LIBS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_DEPS_TARGET
                              aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_aws-sdk-cpp_plugin_scripts"
                              "${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET aws-sdk-cpp::plugin_scripts
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET aws-sdk-cpp::plugin_scripts
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_DEPS_TARGET)
        endif()

        set_property(TARGET aws-sdk-cpp::plugin_scripts APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::plugin_scripts APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::plugin_scripts APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_LIB_DIRS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::plugin_scripts APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET aws-sdk-cpp::plugin_scripts APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT AWS::aws-sdk-cpp-sts #############

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-sts_DEPS_TARGET)
            add_library(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-sts_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_AWS_aws-sdk-cpp-sts_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_LIBS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_AWS_aws-sdk-cpp-sts_DEPS_TARGET
                              aws-sdk-cpp_AWS_aws-sdk-cpp-sts_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_AWS_aws-sdk-cpp-sts"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET AWS::aws-sdk-cpp-sts
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET AWS::aws-sdk-cpp-sts
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_AWS_aws-sdk-cpp-sts_DEPS_TARGET)
        endif()

        set_property(TARGET AWS::aws-sdk-cpp-sts APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-sts APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-sts APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_LIB_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-sts APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-sts APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT AWS::aws-sdk-cpp-sqs #############

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_DEPS_TARGET)
            add_library(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_LIBS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_DEPS_TARGET
                              aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_AWS_aws-sdk-cpp-sqs"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET AWS::aws-sdk-cpp-sqs
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET AWS::aws-sdk-cpp-sqs
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_DEPS_TARGET)
        endif()

        set_property(TARGET AWS::aws-sdk-cpp-sqs APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-sqs APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-sqs APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_LIB_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-sqs APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-sqs APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT AWS::aws-sdk-cpp-s3 #############

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-s3_DEPS_TARGET)
            add_library(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-s3_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_AWS_aws-sdk-cpp-s3_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_LIBS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_AWS_aws-sdk-cpp-s3_DEPS_TARGET
                              aws-sdk-cpp_AWS_aws-sdk-cpp-s3_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_AWS_aws-sdk-cpp-s3"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET AWS::aws-sdk-cpp-s3
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET AWS::aws-sdk-cpp-s3
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_AWS_aws-sdk-cpp-s3_DEPS_TARGET)
        endif()

        set_property(TARGET AWS::aws-sdk-cpp-s3 APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-s3 APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-s3 APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_LIB_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-s3 APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-s3 APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT AWS::aws-sdk-cpp-polly #############

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-polly_DEPS_TARGET)
            add_library(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-polly_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_AWS_aws-sdk-cpp-polly_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_LIBS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_AWS_aws-sdk-cpp-polly_DEPS_TARGET
                              aws-sdk-cpp_AWS_aws-sdk-cpp-polly_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_AWS_aws-sdk-cpp-polly"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET AWS::aws-sdk-cpp-polly
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET AWS::aws-sdk-cpp-polly
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_AWS_aws-sdk-cpp-polly_DEPS_TARGET)
        endif()

        set_property(TARGET AWS::aws-sdk-cpp-polly APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-polly APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-polly APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_LIB_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-polly APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-polly APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT AWS::aws-sdk-cpp-monitoring #############

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_DEPS_TARGET)
            add_library(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_LIBS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_DEPS_TARGET
                              aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET AWS::aws-sdk-cpp-monitoring
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET AWS::aws-sdk-cpp-monitoring
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_DEPS_TARGET)
        endif()

        set_property(TARGET AWS::aws-sdk-cpp-monitoring APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-monitoring APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-monitoring APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_LIB_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-monitoring APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-monitoring APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT AWS::aws-sdk-cpp-kms #############

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-kms_DEPS_TARGET)
            add_library(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-kms_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_AWS_aws-sdk-cpp-kms_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_LIBS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_AWS_aws-sdk-cpp-kms_DEPS_TARGET
                              aws-sdk-cpp_AWS_aws-sdk-cpp-kms_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_AWS_aws-sdk-cpp-kms"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET AWS::aws-sdk-cpp-kms
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET AWS::aws-sdk-cpp-kms
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_AWS_aws-sdk-cpp-kms_DEPS_TARGET)
        endif()

        set_property(TARGET AWS::aws-sdk-cpp-kms APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-kms APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-kms APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_LIB_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-kms APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-kms APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT AWS::aws-sdk-cpp-iam #############

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-iam_DEPS_TARGET)
            add_library(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-iam_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_AWS_aws-sdk-cpp-iam_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_LIBS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_AWS_aws-sdk-cpp-iam_DEPS_TARGET
                              aws-sdk-cpp_AWS_aws-sdk-cpp-iam_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_AWS_aws-sdk-cpp-iam"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET AWS::aws-sdk-cpp-iam
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET AWS::aws-sdk-cpp-iam
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_AWS_aws-sdk-cpp-iam_DEPS_TARGET)
        endif()

        set_property(TARGET AWS::aws-sdk-cpp-iam APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-iam APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-iam APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_LIB_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-iam APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-iam APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT AWS::aws-sdk-cpp-cognito-identity #############

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_DEPS_TARGET)
            add_library(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_LIBS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_DEPS_TARGET
                              aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET AWS::aws-sdk-cpp-cognito-identity
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET AWS::aws-sdk-cpp-cognito-identity
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_DEPS_TARGET)
        endif()

        set_property(TARGET AWS::aws-sdk-cpp-cognito-identity APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-cognito-identity APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-cognito-identity APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_LIB_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-cognito-identity APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-cognito-identity APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_COMPILE_OPTIONS_DEBUG}>)

    ########## COMPONENT AWS::aws-sdk-cpp-core #############

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_FRAMEWORKS_FOUND_DEBUG "")
        conan_find_apple_frameworks(aws-sdk-cpp_AWS_aws-sdk-cpp-core_FRAMEWORKS_FOUND_DEBUG "${aws-sdk-cpp_AWS_aws-sdk-cpp-core_FRAMEWORKS_DEBUG}" "${aws-sdk-cpp_AWS_aws-sdk-cpp-core_FRAMEWORK_DIRS_DEBUG}")

        set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_LIBRARIES_TARGETS "")

        ######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
        if(NOT TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-core_DEPS_TARGET)
            add_library(aws-sdk-cpp_AWS_aws-sdk-cpp-core_DEPS_TARGET INTERFACE IMPORTED)
        endif()

        set_property(TARGET aws-sdk-cpp_AWS_aws-sdk-cpp-core_DEPS_TARGET
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-core_FRAMEWORKS_FOUND_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-core_SYSTEM_LIBS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-core_DEPENDENCIES_DEBUG}>
                     )

        ####### Find the libraries declared in cpp_info.component["xxx"].libs,
        ####### create an IMPORTED target for each one and link the 'aws-sdk-cpp_AWS_aws-sdk-cpp-core_DEPS_TARGET' to all of them
        conan_package_library_targets("${aws-sdk-cpp_AWS_aws-sdk-cpp-core_LIBS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-core_LIB_DIRS_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-core_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-core_LIBRARY_TYPE_DEBUG}"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-core_IS_HOST_WINDOWS_DEBUG}"
                              aws-sdk-cpp_AWS_aws-sdk-cpp-core_DEPS_TARGET
                              aws-sdk-cpp_AWS_aws-sdk-cpp-core_LIBRARIES_TARGETS
                              "_DEBUG"
                              "aws-sdk-cpp_AWS_aws-sdk-cpp-core"
                              "${aws-sdk-cpp_AWS_aws-sdk-cpp-core_NO_SONAME_MODE_DEBUG}")


        ########## TARGET PROPERTIES #####################################
        set_property(TARGET AWS::aws-sdk-cpp-core
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-core_OBJECTS_DEBUG}>
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-core_LIBRARIES_TARGETS}>
                     )

        if("${aws-sdk-cpp_AWS_aws-sdk-cpp-core_LIBS_DEBUG}" STREQUAL "")
            # If the component is not declaring any "cpp_info.components['foo'].libs" the system, frameworks etc are not
            # linked to the imported targets and we need to do it to the global target
            set_property(TARGET AWS::aws-sdk-cpp-core
                         APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                         aws-sdk-cpp_AWS_aws-sdk-cpp-core_DEPS_TARGET)
        endif()

        set_property(TARGET AWS::aws-sdk-cpp-core APPEND PROPERTY INTERFACE_LINK_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-core_LINKER_FLAGS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-core APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-core_INCLUDE_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-core APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-core_LIB_DIRS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-core APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-core_COMPILE_DEFINITIONS_DEBUG}>)
        set_property(TARGET AWS::aws-sdk-cpp-core APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                     $<$<CONFIG:Debug>:${aws-sdk-cpp_AWS_aws-sdk-cpp-core_COMPILE_OPTIONS_DEBUG}>)

    ########## AGGREGATED GLOBAL TARGET WITH THE COMPONENTS #####################
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES aws-sdk-cpp::aws-sdk-cpp-transfer_alias)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES aws-sdk-cpp::aws-sdk-cpp-text-to-speech_alias)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES aws-sdk-cpp::aws-sdk-cpp-s3-encryption_alias)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES aws-sdk-cpp::aws-sdk-cpp-queues_alias)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES aws-sdk-cpp::aws-sdk-cpp-identity-management_alias)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES aws-sdk-cpp::aws-sdk-cpp-access-management_alias)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES AWS::aws-sdk-cpp-transfer)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES AWS::aws-sdk-cpp-text-to-speech)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES aws-sdk-cpp::aws-sdk-cpp-sts_alias)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES aws-sdk-cpp::aws-sdk-cpp-sqs_alias)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES AWS::aws-sdk-cpp-s3-encryption)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES aws-sdk-cpp::aws-sdk-cpp-s3_alias)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES AWS::aws-sdk-cpp-queues)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES aws-sdk-cpp::aws-sdk-cpp-polly_alias)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES aws-sdk-cpp::aws-sdk-cpp-monitoring_alias)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES aws-sdk-cpp::aws-sdk-cpp-kms_alias)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES AWS::aws-sdk-cpp-identity-management)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES aws-sdk-cpp::aws-sdk-cpp-iam_alias)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES aws-sdk-cpp::aws-sdk-cpp-cognito-identity_alias)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES AWS::aws-sdk-cpp-access-management)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES aws-sdk-cpp::plugin_scripts)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES AWS::aws-sdk-cpp-sts)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES AWS::aws-sdk-cpp-sqs)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES AWS::aws-sdk-cpp-s3)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES AWS::aws-sdk-cpp-polly)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES AWS::aws-sdk-cpp-monitoring)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES AWS::aws-sdk-cpp-kms)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES AWS::aws-sdk-cpp-iam)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES AWS::aws-sdk-cpp-cognito-identity)
    set_property(TARGET aws-sdk-cpp::aws-sdk-cpp APPEND PROPERTY INTERFACE_LINK_LIBRARIES AWS::aws-sdk-cpp-core)

########## For the modules (FindXXX)
set(aws-sdk-cpp_LIBRARIES_DEBUG aws-sdk-cpp::aws-sdk-cpp)
