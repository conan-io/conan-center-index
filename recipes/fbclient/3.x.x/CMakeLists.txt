cmake_minimum_required(VERSION 3.1)

project(fbclient VERSION "${CONAN_fbclient_VERSION}" LANGUAGES CXX)

if(NOT WIN32 AND NOT APPLE)
  enable_language(C)
endif()

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS KEEP_RPATHS)

set(root "${PROJECT_SOURCE_DIR}/source_subfolder")
set(src "${root}/src")
set(bin "${PROJECT_BINARY_DIR}")

# ---- Compile checks for config header ----

if(NOT WIN32)
  enable_language(C)
  set(HAVE_ZLIB_H 1)
  if(DEFINED CONAN_CMAKE_SYSTEM_PROCESSOR)
    set(CMAKE_SYSTEM_PROCESSOR "${CONAN_CMAKE_SYSTEM_PROCESSOR}")
  endif()
  include("${root}/builds/cmake/Configure.cmake")

  set(FB_PREFIX "")
  set(FB_IPC_NAME FirebirdIPI)
  set(FB_LOGFILENAME firebird.log)
  set(FB_PIPE_NAME interbas)
  set(FB_SERVICE_NAME gds_db)
  set(FB_SERVICE_PORT 3050)

  # Broken check
  if(NOT GETTIMEOFDAY_RETURNS_TIMEZONE AND NOT TIMEZONE_TYPE STREQUAL "void")
    unset(GETTIMEOFDAY_RETURNS_TIMEZONE CACHE)
    set(TIMEZONE_TYPE void)
    check_prototype_definition(
        gettimeofday
        "int gettimeofday(struct timeval *tv, void *tz)"
        0
        "sys/time.h"
        GETTIMEOFDAY_RETURNS_TIMEZONE
    )
  endif()
endif()

# ---- Dependencies ----

option(THREADS_PREFER_PTHREAD_FLAG "" ON)

find_package(libtommath REQUIRED CONFIG)
find_package(ZLIB REQUIRED CONFIG)
find_package(Threads REQUIRED)

if(APPLE)
  find_package(Iconv REQUIRED CONFIG)

  find_library(FOUNDATION_FRAMEWORK Foundation)
  if(NOT FOUNDATION_FRAMEWORK)
    message(FATAL_ERROR "Foundation not found (${FOUNDATION_FRAMEWORK})")
  endif()

  find_library(SECURITY_FRAMEWORK Security)
  if(NOT SECURITY_FRAMEWORK)
    message(FATAL_ERROR "Security not found (${SECURITY_FRAMEWORK})")
  endif()
endif()

# ---- Library ----

add_library(
    fbclient

    # common
    "${src}/common/Auth.cpp"
    "${src}/common/BigInteger.cpp"
    "${src}/common/DynamicStrings.cpp"
    "${src}/common/IntlParametersBlock.cpp"
    "${src}/common/MsgMetadata.cpp"
    "${src}/common/ScanDir.cpp"
    "${src}/common/StatementMetadata.cpp"
    "${src}/common/StatusArg.cpp"
    "${src}/common/StatusHolder.cpp"
    "${src}/common/ThreadStart.cpp"
    "${src}/common/Tokens.cpp"
    "${src}/common/call_service.cpp"
    "${src}/common/classes/BaseStream.cpp"
    "${src}/common/classes/BlrWriter.cpp"
    "${src}/common/classes/ClumpletReader.cpp"
    "${src}/common/classes/ClumpletWriter.cpp"
    "${src}/common/classes/DbImplementation.cpp"
    "${src}/common/classes/ImplementHelper.cpp"
    "${src}/common/classes/InternalMessageBuffer.cpp"
    "${src}/common/classes/MetaName.cpp"
    "${src}/common/classes/MsgPrint.cpp"
    "${src}/common/classes/NoThrowTimeStamp.cpp"
    "${src}/common/classes/SafeArg.cpp"
    "${src}/common/classes/Synchronize.cpp"
    "${src}/common/classes/TempFile.cpp"
    "${src}/common/classes/alloc.cpp"
    "${src}/common/classes/fb_string.cpp"
    "${src}/common/classes/init.cpp"
    "${src}/common/classes/locks.cpp"
    "${src}/common/classes/semaphore.cpp"
    "${src}/common/classes/timestamp.cpp"
    "${src}/common/config/ConfigCache.cpp"
    "${src}/common/config/config.cpp"
    "${src}/common/config/config_file.cpp"
    "${src}/common/config/dir_list.cpp"
    "${src}/common/cvt.cpp"
    "${src}/common/db_alias.cpp"
    "${src}/common/dllinst.cpp"
    "${src}/common/dsc.cpp"
    "${src}/common/enc.cpp"
    "${src}/common/fb_exception.cpp"
    "${src}/common/isc.cpp"
    "${src}/common/isc_file.cpp"
    "${src}/common/keywords.cpp"
    "${src}/common/sdl.cpp"
    "${src}/common/security.cpp"
    "${src}/common/sha.cpp"
    "${src}/common/sha2/sha2.cpp"
    "${src}/common/utils.cpp"
    "${src}/common/xdr.cpp"
    "${src}/remote/inet.cpp"
    "${src}/remote/merge.cpp"
    "${src}/remote/parser.cpp"
    "${src}/remote/protocol.cpp"
    "${src}/remote/remote.cpp"

    # fbclient
    array.cpp
    blob.cpp
    "${src}/auth/SecureRemotePassword/client/SrpClient.cpp"
    "${src}/auth/SecureRemotePassword/srp.cpp"
    "${src}/auth/SecurityDatabase/LegacyClient.cpp"
    "${src}/plugins/crypt/arc4/Arc4.cpp"
    "${src}/remote/client/BlrFromMessage.cpp"
    "${src}/remote/client/interface.cpp"
    "${src}/yvalve/DistributedTransaction.cpp"
    "${src}/yvalve/MasterImplementation.cpp"
    "${src}/yvalve/PluginManager.cpp"
    "${src}/yvalve/alt.cpp"
    "${src}/yvalve/gds.cpp"
    "${src}/yvalve/keywordsStub.cpp"
    "${src}/yvalve/perf.cpp"
    "${src}/yvalve/preparse.cpp"
    "${src}/yvalve/user_dsql.cpp"
    "${src}/yvalve/utl.cpp"
    "${src}/yvalve/why.cpp"
)

if(MSVC)
  target_compile_options(fbclient PRIVATE /wd4595 /wd4267)
endif()

if(WIN32)
  file(READ "${src}/common/os/win32/mod_loader.cpp" contents)
  # Add support for VS 2019 and VS 2022, they use the same ABI as VS 2015
  string(REPLACE "_MSC_VER < 1920" "_MSC_VER < 1940" contents "${contents}")
  set(out "${bin}/mod_loader.cpp")
  file(WRITE "${out}.tmp" "${contents}")
  execute_process(
      COMMAND "${CMAKE_COMMAND}" -E copy_if_different "${out}.tmp" "${out}"
  )

  target_sources(
      fbclient PRIVATE
      "${out}"
      "${root}/builds/win32/defs/firebird.def"
      "${src}/auth/trusted/AuthSspi.cpp"
      "${src}/common/os/win32/fbsyslog.cpp"
      "${src}/common/os/win32/guid.cpp"
      "${src}/common/os/win32/os_utils.cpp"
      "${src}/common/os/win32/path_utils.cpp"
      "${src}/jrd/os/win32/ibinitdll.cpp"
      "${src}/remote/os/win32/wnet.cpp"
      "${src}/remote/os/win32/xnet.cpp"
      "${src}/yvalve/config/os/win32/config_root.cpp"
  )
  set_source_files_properties(
      "${out}" PROPERTIES
      INCLUDE_DIRECTORIES "${src}/common/os/win32"
  )
  target_link_libraries(fbclient PRIVATE Mpr Ws2_32)
else()
  configure_file(
      "${src}/include/gen/autoconfig.h.in" config_h/gen/autoconfig.h
      @ONLY
  )
  target_include_directories(fbclient PRIVATE "${bin}/config_h")

  target_sources(
      fbclient PRIVATE
      "${src}/common/os/posix/fbsyslog.cpp"
      "${src}/common/os/posix/guid.cpp"
      "${src}/common/os/posix/isc_ipc.cpp"
      "${src}/common/os/posix/os_utils.cpp"
      "${src}/common/os/posix/path_utils.cpp"
  )
  if(APPLE)
    target_sources(
        fbclient PRIVATE
        "${src}/common/os/darwin/mac_utils.m"
        "${src}/common/os/darwin/mod_loader.cpp"
        "${src}/yvalve/config/os/darwin/config_root.cpp"
    )
    target_link_libraries(
        fbclient PRIVATE
        "${FOUNDATION_FRAMEWORK}" "${SECURITY_FRAMEWORK}" Iconv::Iconv
    )
    set_source_files_properties(
        "${src}/common/os/darwin/mac_utils.m" PROPERTIES
        COMPILE_FLAGS "-x objective-c"
    )
  else()
    target_sources(
        fbclient PRIVATE
        "${src}/common/os/posix/mod_loader.cpp"
        "${src}/yvalve/config/os/posix/binreloc.c"
        "${src}/yvalve/config/os/posix/config_root.cpp"
    )
    set_source_files_properties(
        "${src}/yvalve/config/os/posix/binreloc.c" PROPERTIES
        INCLUDE_DIRECTORIES "${bin}/config_h/gen"
    )
  endif()
endif()

if(UNIX)
  target_link_libraries(fbclient PRIVATE m dl)
endif()

target_link_libraries(
    fbclient PRIVATE
    libtommath::libtommath ZLIB::ZLIB Threads::Threads
)

target_include_directories(fbclient PRIVATE "${src}/include")

set_target_properties(
    fbclient PROPERTIES
    VERSION "${PROJECT_VERSION}"
    SOVERSION "${PROJECT_VERSION_MAJOR}"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED YES
)

# ---- Install ----

include(GNUInstallDirs)

install(
    TARGETS fbclient
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
)

foreach(file "${src}/jrd/ibase.h" "${src}/yvalve/perf.h")
  get_filename_component(basename "${file}" NAME)
  file(READ "${file}" content)
  string(REGEX REPLACE [[(#include ")\.\./[^/]+/]] "\\1" content "${content}")
  set(out "${bin}/${basename}")
  file(WRITE "${out}.tmp" "${content}")
  execute_process(
      COMMAND "${CMAKE_COMMAND}" -E copy_if_different "${out}.tmp" "${out}"
  )
  install(FILES "${out}" DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}")
endforeach()

install(
    FILES
    "${src}/common/dsc_pub.h"
    "${src}/dsql/sqlda_pub.h"
    "${src}/extlib/ib_util.h"
    "${src}/include/consts_pub.h"
    "${src}/include/types_pub.h"
    "${src}/include/gen/iberror.h"
    "${src}/jrd/blr.h"
    "${src}/jrd/inf_pub.h"
    "${src}/yvalve/perf_proto.h"
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)
