########### AGGREGATED COMPONENTS AND DEPENDENCIES FOR THE MULTI CONFIG #####################
#############################################################################################

set(zlib_COMPONENT_NAMES "")
if(DEFINED zlib_FIND_DEPENDENCY_NAMES)
  list(APPEND zlib_FIND_DEPENDENCY_NAMES )
  list(REMOVE_DUPLICATES zlib_FIND_DEPENDENCY_NAMES)
else()
  set(zlib_FIND_DEPENDENCY_NAMES )
endif()

########### VARIABLES #######################################################################
#############################################################################################
set(zlib_PACKAGE_FOLDER_DEBUG "C:/Users/MH.Rezaiy_110/.conan2/p/b/zlib26778d26a6241/p")
set(zlib_BUILD_MODULES_PATHS_DEBUG )


set(zlib_INCLUDE_DIRS_DEBUG )
set(zlib_RES_DIRS_DEBUG )
set(zlib_DEFINITIONS_DEBUG )
set(zlib_SHARED_LINK_FLAGS_DEBUG )
set(zlib_EXE_LINK_FLAGS_DEBUG )
set(zlib_OBJECTS_DEBUG )
set(zlib_COMPILE_DEFINITIONS_DEBUG )
set(zlib_COMPILE_OPTIONS_C_DEBUG )
set(zlib_COMPILE_OPTIONS_CXX_DEBUG )
set(zlib_LIB_DIRS_DEBUG "${zlib_PACKAGE_FOLDER_DEBUG}/lib")
set(zlib_BIN_DIRS_DEBUG )
set(zlib_LIBRARY_TYPE_DEBUG STATIC)
set(zlib_IS_HOST_WINDOWS_DEBUG 1)
set(zlib_LIBS_DEBUG zlib)
set(zlib_SYSTEM_LIBS_DEBUG )
set(zlib_FRAMEWORK_DIRS_DEBUG )
set(zlib_FRAMEWORKS_DEBUG )
set(zlib_BUILD_DIRS_DEBUG )
set(zlib_NO_SONAME_MODE_DEBUG FALSE)


# COMPOUND VARIABLES
set(zlib_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${zlib_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${zlib_COMPILE_OPTIONS_C_DEBUG}>")
set(zlib_LINKER_FLAGS_DEBUG
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${zlib_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${zlib_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${zlib_EXE_LINK_FLAGS_DEBUG}>")


set(zlib_COMPONENTS_DEBUG )