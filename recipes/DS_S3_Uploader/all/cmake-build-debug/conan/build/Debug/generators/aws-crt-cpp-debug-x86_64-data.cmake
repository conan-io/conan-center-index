########### AGGREGATED COMPONENTS AND DEPENDENCIES FOR THE MULTI CONFIG #####################
#############################################################################################

set(aws-crt-cpp_COMPONENT_NAMES "")
if(DEFINED aws-crt-cpp_FIND_DEPENDENCY_NAMES)
  list(APPEND aws-crt-cpp_FIND_DEPENDENCY_NAMES aws-c-s3 aws-c-auth aws-c-event-stream aws-c-mqtt aws-c-http aws-c-compression aws-c-io aws-c-cal aws-c-sdkutils aws-checksums aws-c-common)
  list(REMOVE_DUPLICATES aws-crt-cpp_FIND_DEPENDENCY_NAMES)
else()
  set(aws-crt-cpp_FIND_DEPENDENCY_NAMES aws-c-s3 aws-c-auth aws-c-event-stream aws-c-mqtt aws-c-http aws-c-compression aws-c-io aws-c-cal aws-c-sdkutils aws-checksums aws-c-common)
endif()
set(aws-c-s3_FIND_MODE "NO_MODULE")
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

########### VARIABLES #######################################################################
#############################################################################################
set(aws-crt-cpp_PACKAGE_FOLDER_DEBUG "C:/Users/MH.Rezaiy_110/.conan2/p/b/aws-c19ff89fd7e508/p")
set(aws-crt-cpp_BUILD_MODULES_PATHS_DEBUG )


set(aws-crt-cpp_INCLUDE_DIRS_DEBUG "${aws-crt-cpp_PACKAGE_FOLDER_DEBUG}/include")
set(aws-crt-cpp_RES_DIRS_DEBUG )
set(aws-crt-cpp_DEFINITIONS_DEBUG )
set(aws-crt-cpp_SHARED_LINK_FLAGS_DEBUG )
set(aws-crt-cpp_EXE_LINK_FLAGS_DEBUG )
set(aws-crt-cpp_OBJECTS_DEBUG )
set(aws-crt-cpp_COMPILE_DEFINITIONS_DEBUG )
set(aws-crt-cpp_COMPILE_OPTIONS_C_DEBUG )
set(aws-crt-cpp_COMPILE_OPTIONS_CXX_DEBUG )
set(aws-crt-cpp_LIB_DIRS_DEBUG "${aws-crt-cpp_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-crt-cpp_BIN_DIRS_DEBUG )
set(aws-crt-cpp_LIBRARY_TYPE_DEBUG STATIC)
set(aws-crt-cpp_IS_HOST_WINDOWS_DEBUG 1)
set(aws-crt-cpp_LIBS_DEBUG aws-crt-cpp)
set(aws-crt-cpp_SYSTEM_LIBS_DEBUG )
set(aws-crt-cpp_FRAMEWORK_DIRS_DEBUG )
set(aws-crt-cpp_FRAMEWORKS_DEBUG )
set(aws-crt-cpp_BUILD_DIRS_DEBUG )
set(aws-crt-cpp_NO_SONAME_MODE_DEBUG FALSE)


# COMPOUND VARIABLES
set(aws-crt-cpp_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-crt-cpp_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-crt-cpp_COMPILE_OPTIONS_C_DEBUG}>")
set(aws-crt-cpp_LINKER_FLAGS_DEBUG
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-crt-cpp_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-crt-cpp_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-crt-cpp_EXE_LINK_FLAGS_DEBUG}>")


set(aws-crt-cpp_COMPONENTS_DEBUG )