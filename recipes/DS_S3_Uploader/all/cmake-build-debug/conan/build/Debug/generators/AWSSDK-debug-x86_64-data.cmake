########### AGGREGATED COMPONENTS AND DEPENDENCIES FOR THE MULTI CONFIG #####################
#############################################################################################

list(APPEND aws-sdk-cpp_COMPONENT_NAMES AWS::aws-sdk-cpp-core AWS::aws-sdk-cpp-cognito-identity AWS::aws-sdk-cpp-iam AWS::aws-sdk-cpp-kms AWS::aws-sdk-cpp-monitoring AWS::aws-sdk-cpp-polly AWS::aws-sdk-cpp-s3 AWS::aws-sdk-cpp-sqs AWS::aws-sdk-cpp-sts aws-sdk-cpp::plugin_scripts AWS::aws-sdk-cpp-access-management aws-sdk-cpp::aws-sdk-cpp-cognito-identity_alias aws-sdk-cpp::aws-sdk-cpp-iam_alias AWS::aws-sdk-cpp-identity-management aws-sdk-cpp::aws-sdk-cpp-kms_alias aws-sdk-cpp::aws-sdk-cpp-monitoring_alias aws-sdk-cpp::aws-sdk-cpp-polly_alias AWS::aws-sdk-cpp-queues aws-sdk-cpp::aws-sdk-cpp-s3_alias AWS::aws-sdk-cpp-s3-encryption aws-sdk-cpp::aws-sdk-cpp-sqs_alias aws-sdk-cpp::aws-sdk-cpp-sts_alias AWS::aws-sdk-cpp-text-to-speech AWS::aws-sdk-cpp-transfer aws-sdk-cpp::aws-sdk-cpp-access-management_alias aws-sdk-cpp::aws-sdk-cpp-identity-management_alias aws-sdk-cpp::aws-sdk-cpp-queues_alias aws-sdk-cpp::aws-sdk-cpp-s3-encryption_alias aws-sdk-cpp::aws-sdk-cpp-text-to-speech_alias aws-sdk-cpp::aws-sdk-cpp-transfer_alias)
list(REMOVE_DUPLICATES aws-sdk-cpp_COMPONENT_NAMES)
if(DEFINED aws-sdk-cpp_FIND_DEPENDENCY_NAMES)
  list(APPEND aws-sdk-cpp_FIND_DEPENDENCY_NAMES aws-crt-cpp aws-c-auth aws-c-event-stream aws-c-mqtt aws-c-http aws-c-compression aws-c-io aws-c-cal aws-c-sdkutils aws-checksums aws-c-common ZLIB)
  list(REMOVE_DUPLICATES aws-sdk-cpp_FIND_DEPENDENCY_NAMES)
else()
  set(aws-sdk-cpp_FIND_DEPENDENCY_NAMES aws-crt-cpp aws-c-auth aws-c-event-stream aws-c-mqtt aws-c-http aws-c-compression aws-c-io aws-c-cal aws-c-sdkutils aws-checksums aws-c-common ZLIB)
endif()
set(aws-crt-cpp_FIND_MODE "NO_MODULE")
set(aws-c-auth_FIND_MODE "NO_MODULE")
set(aws-c-event-stream_FIND_MODE "NO_MODULE")
set(aws-c-mqtt_FIND_MODE "NO_MODULE")
set(aws-c-http_FIND_MODE "NO_MODULE")
set(aws-c-compression_FIND_MODE "NO_MODULE")
set(aws-c-io_FIND_MODE "NO_MODULE")
set(aws-c-cal_FIND_MODE "NO_MODULE")
set(aws-c-sdkutils_FIND_MODE "NO_MODULE")
set(aws-checksums_FIND_MODE "NO_MODULE")
set(aws-c-common_FIND_MODE "NO_MODULE")
set(ZLIB_FIND_MODE "NO_MODULE")

########### VARIABLES #######################################################################
#############################################################################################
set(aws-sdk-cpp_PACKAGE_FOLDER_DEBUG "C:/Users/MH.Rezaiy_110/.conan2/p/b/aws-s86d2422903e99/p")
set(aws-sdk-cpp_BUILD_MODULES_PATHS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/res/cmake/sdk_plugin_conf.cmake")


set(aws-sdk-cpp_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_RES_DIRS_DEBUG )
set(aws-sdk-cpp_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_OBJECTS_DEBUG )
set(aws-sdk-cpp_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_COMPILE_OPTIONS_C_DEBUG )
set(aws-sdk-cpp_COMPILE_OPTIONS_CXX_DEBUG )
set(aws-sdk-cpp_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_LIBS_DEBUG aws-cpp-sdk-transfer aws-cpp-sdk-text-to-speech aws-cpp-sdk-s3-encryption aws-cpp-sdk-queues aws-cpp-sdk-identity-management aws-cpp-sdk-access-management aws-cpp-sdk-sts aws-cpp-sdk-sqs aws-cpp-sdk-s3 aws-cpp-sdk-polly aws-cpp-sdk-monitoring aws-cpp-sdk-kms aws-cpp-sdk-iam aws-cpp-sdk-cognito-identity aws-cpp-sdk-core)
set(aws-sdk-cpp_SYSTEM_LIBS_DEBUG winmm winhttp wininet bcrypt userenv version ws2_32)
set(aws-sdk-cpp_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_BUILD_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/res/cmake"
			"${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/res/toolchains")
set(aws-sdk-cpp_NO_SONAME_MODE_DEBUG FALSE)


# COMPOUND VARIABLES
set(aws-sdk-cpp_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_COMPILE_OPTIONS_C_DEBUG}>")
set(aws-sdk-cpp_LINKER_FLAGS_DEBUG
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_EXE_LINK_FLAGS_DEBUG}>")


set(aws-sdk-cpp_COMPONENTS_DEBUG AWS::aws-sdk-cpp-core AWS::aws-sdk-cpp-cognito-identity AWS::aws-sdk-cpp-iam AWS::aws-sdk-cpp-kms AWS::aws-sdk-cpp-monitoring AWS::aws-sdk-cpp-polly AWS::aws-sdk-cpp-s3 AWS::aws-sdk-cpp-sqs AWS::aws-sdk-cpp-sts aws-sdk-cpp::plugin_scripts AWS::aws-sdk-cpp-access-management aws-sdk-cpp::aws-sdk-cpp-cognito-identity_alias aws-sdk-cpp::aws-sdk-cpp-iam_alias AWS::aws-sdk-cpp-identity-management aws-sdk-cpp::aws-sdk-cpp-kms_alias aws-sdk-cpp::aws-sdk-cpp-monitoring_alias aws-sdk-cpp::aws-sdk-cpp-polly_alias AWS::aws-sdk-cpp-queues aws-sdk-cpp::aws-sdk-cpp-s3_alias AWS::aws-sdk-cpp-s3-encryption aws-sdk-cpp::aws-sdk-cpp-sqs_alias aws-sdk-cpp::aws-sdk-cpp-sts_alias AWS::aws-sdk-cpp-text-to-speech AWS::aws-sdk-cpp-transfer aws-sdk-cpp::aws-sdk-cpp-access-management_alias aws-sdk-cpp::aws-sdk-cpp-identity-management_alias aws-sdk-cpp::aws-sdk-cpp-queues_alias aws-sdk-cpp::aws-sdk-cpp-s3-encryption_alias aws-sdk-cpp::aws-sdk-cpp-text-to-speech_alias aws-sdk-cpp::aws-sdk-cpp-transfer_alias)
########### COMPONENT aws-sdk-cpp::aws-sdk-cpp-transfer_alias VARIABLES ############################################

set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_RES_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_OBJECTS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-transfer)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-transfer_alias_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT aws-sdk-cpp::aws-sdk-cpp-text-to-speech_alias VARIABLES ############################################

set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_RES_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_OBJECTS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-text-to-speech)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-text-to-speech_alias_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT aws-sdk-cpp::aws-sdk-cpp-s3-encryption_alias VARIABLES ############################################

set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_RES_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_OBJECTS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-s3-encryption)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3-encryption_alias_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT aws-sdk-cpp::aws-sdk-cpp-queues_alias VARIABLES ############################################

set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_RES_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_OBJECTS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-queues)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-queues_alias_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT aws-sdk-cpp::aws-sdk-cpp-identity-management_alias VARIABLES ############################################

set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_RES_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_OBJECTS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-identity-management)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-identity-management_alias_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT aws-sdk-cpp::aws-sdk-cpp-access-management_alias VARIABLES ############################################

set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_RES_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_OBJECTS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-access-management)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-access-management_alias_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT AWS::aws-sdk-cpp-transfer VARIABLES ############################################

set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_RES_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_OBJECTS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_LIBS_DEBUG aws-cpp-sdk-transfer)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-core AWS::aws-sdk-cpp-s3)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_AWS_aws-sdk-cpp-transfer_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT AWS::aws-sdk-cpp-text-to-speech VARIABLES ############################################

set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_RES_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_OBJECTS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_LIBS_DEBUG aws-cpp-sdk-text-to-speech)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_SYSTEM_LIBS_DEBUG winmm)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-core AWS::aws-sdk-cpp-polly)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_AWS_aws-sdk-cpp-text-to-speech_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT aws-sdk-cpp::aws-sdk-cpp-sts_alias VARIABLES ############################################

set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_RES_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_OBJECTS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-sts)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sts_alias_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT aws-sdk-cpp::aws-sdk-cpp-sqs_alias VARIABLES ############################################

set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_RES_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_OBJECTS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-sqs)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-sqs_alias_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT AWS::aws-sdk-cpp-s3-encryption VARIABLES ############################################

set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_RES_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_OBJECTS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_LIBS_DEBUG aws-cpp-sdk-s3-encryption)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-core AWS::aws-sdk-cpp-s3 AWS::aws-sdk-cpp-kms)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3-encryption_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT aws-sdk-cpp::aws-sdk-cpp-s3_alias VARIABLES ############################################

set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_RES_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_OBJECTS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-s3)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-s3_alias_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT AWS::aws-sdk-cpp-queues VARIABLES ############################################

set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_RES_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_OBJECTS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_LIBS_DEBUG aws-cpp-sdk-queues)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-core AWS::aws-sdk-cpp-sqs)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-queues_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_AWS_aws-sdk-cpp-queues_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT aws-sdk-cpp::aws-sdk-cpp-polly_alias VARIABLES ############################################

set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_RES_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_OBJECTS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-polly)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-polly_alias_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT aws-sdk-cpp::aws-sdk-cpp-monitoring_alias VARIABLES ############################################

set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_RES_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_OBJECTS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-monitoring)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-monitoring_alias_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT aws-sdk-cpp::aws-sdk-cpp-kms_alias VARIABLES ############################################

set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_RES_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_OBJECTS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-kms)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-kms_alias_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT AWS::aws-sdk-cpp-identity-management VARIABLES ############################################

set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_RES_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_OBJECTS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_LIBS_DEBUG aws-cpp-sdk-identity-management)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-core AWS::aws-sdk-cpp-cognito-identity AWS::aws-sdk-cpp-sts)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_AWS_aws-sdk-cpp-identity-management_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT aws-sdk-cpp::aws-sdk-cpp-iam_alias VARIABLES ############################################

set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_RES_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_OBJECTS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-iam)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-iam_alias_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT aws-sdk-cpp::aws-sdk-cpp-cognito-identity_alias VARIABLES ############################################

set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_RES_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_OBJECTS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-cognito-identity)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_aws-sdk-cpp_aws-sdk-cpp-cognito-identity_alias_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT AWS::aws-sdk-cpp-access-management VARIABLES ############################################

set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_RES_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_OBJECTS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_LIBS_DEBUG aws-cpp-sdk-access-management)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-core AWS::aws-sdk-cpp-iam AWS::aws-sdk-cpp-cognito-identity)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_AWS_aws-sdk-cpp-access-management_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT aws-sdk-cpp::plugin_scripts VARIABLES ############################################

set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_RES_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_OBJECTS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-core)
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_aws-sdk-cpp_plugin_scripts_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT AWS::aws-sdk-cpp-sts VARIABLES ############################################

set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_RES_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_OBJECTS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_LIBS_DEBUG aws-cpp-sdk-sts)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-core)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sts_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sts_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT AWS::aws-sdk-cpp-sqs VARIABLES ############################################

set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_RES_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_OBJECTS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_LIBS_DEBUG aws-cpp-sdk-sqs)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-core)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_AWS_aws-sdk-cpp-sqs_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT AWS::aws-sdk-cpp-s3 VARIABLES ############################################

set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_RES_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_OBJECTS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_LIBS_DEBUG aws-cpp-sdk-s3)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-core)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-s3_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_AWS_aws-sdk-cpp-s3_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT AWS::aws-sdk-cpp-polly VARIABLES ############################################

set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_RES_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_OBJECTS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_LIBS_DEBUG aws-cpp-sdk-polly)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-core)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-polly_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_AWS_aws-sdk-cpp-polly_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT AWS::aws-sdk-cpp-monitoring VARIABLES ############################################

set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_RES_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_OBJECTS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_LIBS_DEBUG aws-cpp-sdk-monitoring)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-core)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_AWS_aws-sdk-cpp-monitoring_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT AWS::aws-sdk-cpp-kms VARIABLES ############################################

set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_RES_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_OBJECTS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_LIBS_DEBUG aws-cpp-sdk-kms)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-core)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-kms_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_AWS_aws-sdk-cpp-kms_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT AWS::aws-sdk-cpp-iam VARIABLES ############################################

set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_RES_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_OBJECTS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_LIBS_DEBUG aws-cpp-sdk-iam)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-core)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-iam_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_AWS_aws-sdk-cpp-iam_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT AWS::aws-sdk-cpp-cognito-identity VARIABLES ############################################

set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_RES_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_OBJECTS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_LIBS_DEBUG aws-cpp-sdk-cognito-identity)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_SYSTEM_LIBS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_DEPENDENCIES_DEBUG AWS::aws-sdk-cpp-core)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_AWS_aws-sdk-cpp-cognito-identity_COMPILE_OPTIONS_C_DEBUG}>")
########### COMPONENT AWS::aws-sdk-cpp-core VARIABLES ############################################

set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_INCLUDE_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_LIB_DIRS_DEBUG "${aws-sdk-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_BIN_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_LIBRARY_TYPE_DEBUG STATIC)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_IS_HOST_WINDOWS_DEBUG 1)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_RES_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_OBJECTS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_COMPILE_DEFINITIONS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_COMPILE_OPTIONS_C_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_COMPILE_OPTIONS_CXX_DEBUG "")
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_LIBS_DEBUG aws-cpp-sdk-core)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_SYSTEM_LIBS_DEBUG winhttp wininet bcrypt userenv version ws2_32)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_FRAMEWORK_DIRS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_FRAMEWORKS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_DEPENDENCIES_DEBUG AWS::aws-crt-cpp AWS::aws-c-auth AWS::aws-c-cal AWS::aws-c-common AWS::aws-c-compression AWS::aws-c-event-stream AWS::aws-c-http AWS::aws-c-io AWS::aws-c-mqtt AWS::aws-checksums ZLIB::ZLIB AWS::aws-c-sdkutils)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_SHARED_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_EXE_LINK_FLAGS_DEBUG )
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_NO_SONAME_MODE_DEBUG FALSE)

# COMPOUND VARIABLES
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_LINKER_FLAGS_DEBUG
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-core_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-sdk-cpp_AWS_aws-sdk-cpp-core_SHARED_LINK_FLAGS_DEBUG}>
        $<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-sdk-cpp_AWS_aws-sdk-cpp-core_EXE_LINK_FLAGS_DEBUG}>
)
set(aws-sdk-cpp_AWS_aws-sdk-cpp-core_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-sdk-cpp_AWS_aws-sdk-cpp-core_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-sdk-cpp_AWS_aws-sdk-cpp-core_COMPILE_OPTIONS_C_DEBUG}>")