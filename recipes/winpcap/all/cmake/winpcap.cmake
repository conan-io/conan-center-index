cmake_minimum_required(VERSION 3.3)
project(winpcap C)


if(UNIX AND NOT (WIN32 OR APPLE))
    set(LINUX ON)
else()
    set(LINUX OFF)
endif()

if(CMAKE_C_COMPILER_ID MATCHES "^MSVC$")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -nologo")
elseif(CMAKE_C_COMPILER_ID MATCHES "^AppleClang$")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fno-common")
endif()

include(CheckCSourceCompiles)
include(CheckFunctionExists)
include(CheckIncludeFile)
include(CheckIncludeFiles)
include(CheckLibraryExists)
include(CheckSymbolExists)
include(CheckTypeSize)
include(CMakeDependentOption)
include(CMakePushCheckState)
include(GNUInstallDirs)

option(WINPCAP_BUGGY_TM_SUPPORT "Build winpcap with buggy time support")
option(WINPCAP_IPV6 "Enable ipv6 support" ON)
cmake_dependent_option(WINPCAP_LFS "Enable Large File Support" ON "NOT WIN32" OFF)
option(WINPCAP_PROTOCHAIN "Enable protochain support")
option(WINPCAP_REMOTE "Enable remote capture capabilities" ON)
option(WINPCAP_TURBOCAP "Enable support for turbocap adapters" ON)
cmake_dependent_option(WINPCAP_USB "Support USB sniffing" ON LINUX OFF)
set(WINPCAP_USB_DEVICE "" CACHE STRING "path for device for USB sniffing")

if(WIN32)
    set(WINPCAP_CAPTURE_TYPE_DEFAULT win32)
elseif(LINUX)
    set(WINPCAP_CAPTURE_TYPE_DEFAULT linux)
else()
    set(WINPCAP_CAPTURE_TYPE_DEFAULT null)
endif()

set(WINPCAP_CAPTURE_TYPES bpf dag dlpi enet nit null libdlpi linux pf sita snit snoop win32)
set(WINPCAP_CAPTURE_TYPE "${WINPCAP_CAPTURE_TYPE_DEFAULT}" CACHE STRING "WinPcap capture type")
set_property(CACHE WINPCAP_CAPTURE_TYPE PROPERTY STRINGS ${WINPCAP_CAPTURE_TYPES})
if(NOT WINPCAP_CAPTURE_TYPE IN_LIST WINPCAP_CAPTURE_TYPES)
    message(FATAL_ERROR "Invalid WINPCAP_CAPTURE_TYPE=${WINPCAP_CAPTURE_TYPE} (choices=${WINPCAP_CAPTURE_TYPES})")
endif()

message(STATUS "WINPCAP_BUGGY_TM_SUPPORT:   ${WINPCAP_BUGGY_TM_SUPPORT}")
message(STATUS "WINPCAP_CAPTURE_TYPE:       ${WINPCAP_CAPTURE_TYPE}         (choices=${WINPCAP_CAPTURE_TYPES})")
message(STATUS "WINPCAP_IPV6:               ${WINPCAP_IPV6}")
message(STATUS "WINPCAP_LFS:                ${WINPCAP_LFS}")
message(STATUS "WINPCAP_PROTOCHAIN:         ${WINPCAP_PROTOCHAIN}")
message(STATUS "WINPCAP_REMOTE:             ${WINPCAP_REMOTE}")
message(STATUS "WINPCAP_TURBOCAP:           ${WINPCAP_TURBOCAP}")

set(WINPCAP_HAVE_DEFINES)
set(WINPCAP_LIBRARIES)

function(winpcap_check_include_file HEADER VARIABLE DEFINITIONS)
    cmake_reset_check_state()
    set(CMAKE_REQUIRED_DEFINITIONS)
    foreach(def ${DEFINITIONS})
        list(APPEND CMAKE_REQUIRED_DEFINITIONS "-D${def}")
    endforeach()
    check_include_file("${HEADER}" "${VARIABLE}")
    if(DEFINITIONS AND ${VARIABLE})
        list(APPEND ${DEFINITIONS} ${VARIABLE})
        set(${DEFINITIONS} "${${DEFINITIONS}}" PARENT_SCOPE)
    endif()
endfunction()

function(winpcap_check_include_files HEADERS VARIABLE DEFINITIONS)
    cmake_reset_check_state()
    set(CMAKE_REQUIRED_DEFINITIONS)
    foreach(def ${DEFINITIONS})
        list(APPEND CMAKE_REQUIRED_DEFINITIONS "-D${def}")
    endforeach()
    check_include_files("${HEADERS}" "${VARIABLE}")
    if(DEFINITIONS AND ${VARIABLE})
        list(APPEND ${DEFINITIONS} ${VARIABLE})
        set(${DEFINITIONS} "${${DEFINITIONS}}" PARENT_SCOPE)
    endif()
endfunction()

function(winpcap_check_c_source_compiles SOURCE VARIABLE DEFINITIONS)
    cmake_reset_check_state()
    set(CMAKE_REQUIRED_DEFINITIONS)
    foreach(def ${DEFINITIONS})
        list(APPEND CMAKE_REQUIRED_DEFINITIONS "-D${def}")
    endforeach()
    check_c_source_compiles("${SOURCE}" "${VARIABLE}")
    if(DEFINITIONS AND ${VARIABLE})
        list(APPEND ${DEFINITIONS} ${VARIABLE})
        set(${DEFINITIONS} "${${DEFINITIONS}}" PARENT_SCOPE)
    endif()
endfunction()

function(winpcap_check_function_exists FUNCTION VARIABLE DEFINITIONS)
    cmake_reset_check_state()
    set(CMAKE_REQUIRED_DEFINITIONS)
    foreach(def ${DEFINITIONS})
        list(APPEND CMAKE_REQUIRED_DEFINITIONS "-D${def}")
    endforeach()
    check_function_exists("${FUNCTION}" "${VARIABLE}")
    if(DEFINITIONS AND ${VARIABLE})
        list(APPEND ${DEFINITIONS} ${VARIABLE})
        set(${DEFINITIONS} "${${DEFINITIONS}}" PARENT_SCOPE)
    endif()
endfunction()

function(winpcap_check_symbol_exists FUNCTION HEADERS VARIABLE DEFINITIONS)
    cmake_reset_check_state()
    set(CMAKE_REQUIRED_DEFINITIONS)
    foreach(def ${DEFINITIONS})
        list(APPEND CMAKE_REQUIRED_DEFINITIONS "-D${def}")
    endforeach()
    check_symbol_exists("${FUNCTION}" "${HEADERS}" "${VARIABLE}")
    if(DEFINITIONS AND ${VARIABLE})
        list(APPEND ${DEFINITIONS} ${VARIABLE})
        set(${DEFINITIONS} "${${DEFINITIONS}}" PARENT_SCOPE)
    endif()
endfunction()

function(winpcap_check_type TYPE VARIABLE DEFINITIONS)
    cmake_reset_check_state()
    set(CMAKE_REQUIRED_DEFINITIONS)
    foreach(def ${DEFINITIONS})
        list(APPEND CMAKE_REQUIRED_DEFINITIONS "-D${def}")
    endforeach()
    set(src [[
        #include <sys/types.h>
        #if STDC_HEADERS
        # include <stdlib.h>
        # include <stddef.h>
        #endif
        __TYPE__ i;
    ]])
    string(REPLACE __TYPE__ "${TYPE}" src "${src}")
    winpcap_check_c_source_compiles("${src}" ${VARIABLE} "${DEFINITIONS}")
    if(DEFINITIONS AND ${VARIABLE})
        list(APPEND ${DEFINITIONS} ${VARIABLE})
        set(${DEFINITIONS} "${${DEFINITIONS}}" PARENT_SCOPE)
    endif()
endfunction()

function(winpcap_find_library_containing_symbol LIBRARIES FUNCTION FOUND LIBRARY DEFINITIONS LIBS)
    cmake_reset_check_state()
    set(CMAKE_REQUIRED_DEFINITIONS)
    foreach(def ${DEFINITIONS})
        list(APPEND CMAKE_REQUIRED_DEFINITIONS "-D${def}")
    endforeach()
    if(LIBS)
        set(CMAKE_REQUIRED_LIBRARIES ${LIBS})
    endif()
    set(libfound OFF)
    foreach(library ${LIBRARIES})
        if(NOT libfound)
            check_library_exists("${library}" "${FUNCTION}" "" "${library}_HAS_${FUNCTION}")
            if(${library}_HAS_${FUNCTION})
                set(libfound ON)
                set(library "${library}")
            endif()
        endif()
    endforeach()
    set(${FOUND} ${libfound} PARENT_SCOPE)
    if(libfound)
        set(${LIBRARY} "${library}" PARENT_SCOPE)
    endif()
endfunction()

cmake_reset_check_state()
check_type_size(char SIZEOF_CHAR)
if(HAVE_SIZEOF_CHAR)
    list(APPEND WINPCAP_HAVE_DEFINES SIZEOF_CHAR=${SIZEOF_CHAR})
endif()

check_type_size(short SIZEOF_SHORT)
if(HAVE_SIZEOF_SHORT)
    list(APPEND WINPCAP_HAVE_DEFINES SIZEOF_SHORT=${SIZEOF_SHORT})
endif()

check_type_size(int SIZEOF_INT)
if(HAVE_SIZEOF_INT)
    list(APPEND WINPCAP_HAVE_DEFINES SIZEOF_INT=${SIZEOF_INT})
endif()

check_type_size(long SIZEOF_LONG)
if(HAVE_SIZEOF_LONG)
    list(APPEND WINPCAP_HAVE_DEFINES SIZEOF_LONG=${SIZEOF_LONG})
endif()

check_type_size("long long" SIZEOF_LONG_LONG)
if(HAVE_SIZEOF_LONG_LONG)
    list(APPEND WINPCAP_HAVE_DEFINES SIZEOF_LONG_LONG=${SIZEOF_LONG_LONG})
endif()

cmake_reset_check_state()
check_c_source_compiles([[
        static void foo(void) __attribute__ ((noreturn));
        static void foo(void) {
            return;
        }
        int main(int argc, char **argv) {
            foo();
        }
    ]] HAVE___ATTRIBUTE__)
if(HAVE___ATTRIBUTE__)
    list(APPEND WINPCAP_HAVE_DEFINES
        HAVE___ATTRIBUTE__
        "_U_=__attribute__((unused))"
    )
else()
    list(APPEND WINPCAP_HAVE_DEFINES "_U_=")
endif()

cmake_reset_check_state()
check_c_source_compiles([[
        #include <sys/types.h>
        #include <sys/socket.h>
        int main() {
            socklen_t x;
        }
    ]] HAVE_SOCKLEN_T)
if(HAVE_SOCKLEN_T)
    list(APPEND WINPCAP_HAVE_DEFINES HAVE_SOCKLEN_T)
endif()

cmake_reset_check_state()
check_symbol_exists(SIOCGSTAMP "linux/sockios.h" NEED_LINUX_SOCKIOS_H)
if(NEED_LINUX_SOCKIOS_H)
    list(APPEND WINPCAP_HAVE_DEFINES NEED_LINUX_SOCKIOS_H)
endif()

winpcap_check_include_file("sys/ioccom.h" HAVE_SYS_IOCCOM_H WINPCAP_HAVE_DEFINES)
winpcap_check_include_file("sys/sockio.h" HAVE_SYS_SOCKIO_H WINPCAP_HAVE_DEFINES)
winpcap_check_include_file("limits.h" HAVE_LIMITS_H WINPCAP_HAVE_DEFINES)
winpcap_check_include_file("paths.h" HAVE_PATHS_H WINPCAP_HAVE_DEFINES)

winpcap_check_include_files("sys/types.h;sys/socket.h;net/if.h;net/pfvar.h" HAVE_NET_PFVAR_H WINPCAP_HAVE_DEFINES)
if(HAVE_NET_PFVAR_H)
    winpcap_check_c_source_compiles([[
        #include <sys/types.h>
        #include <sys/socket.h>
        #include <net/if.h>
        #include <net/pfvar.h>
        int main() {
            return PF_NAT+PF_NONAT+PF_BINAT+PF_NOBINAT+PF_RDR+PF_NORDR;
        }
    ]] HAVE_PF_NAT_THROUGH_PF_NORDR WINPCAP_HAVE_DEFINES)
endif()

check_include_file("netinit/if_ether.h" HAVE_NETINIT_IF_ETHER_H)
if(NOT HAVE_NETINIT_IF_ETHER_H)
    winpcap_check_c_source_compiles([[
        #include <sys/socket.h>
        #include <netinet/in.h>
        struct mbuf;
        struct rtentry;
        #include <net/if.h>
        #include <netinit/if_ether.h>
    ]] HAVE_NETINIT_IF_ETHER_H WINPCAP_HAVE_DEFINES)
endif()

if(CMAKE_C_COMPILER_ID MATCHES "^(GNU|Clang)$")
    set(tmpdefines ${WINPCAP_HAVE_DEFINES})
    winpcap_check_c_source_compiles([[
            #include <sys/types.h>
            #include <sys/time.h>
            #include <sys/ioctl.h>
            #ifdef HAVE_SYS_IOCCOM_H
            #include <sys/ioccom.h>
            #endif
            int main() {
                switch (0) {
                    case _IO('A', 1):;
                    case _IO('B', 1):;
                }
            }
        ]] GCC_FIXINCLUDES tmpdefines)
    if(NOT GCC_FIXINCLUDES)
        message(FATAL_ERROR "see the INSTALL for more info")
    endif()
endif()

winpcap_check_symbol_exists(strerror string.h HAVE_STRERROR WINPCAP_HAVE_DEFINES)
winpcap_check_symbol_exists(strlcpy string.h HAVE_STRERROR WINPCAP_HAVE_DEFINES)

winpcap_check_symbol_exists(snprintf stdio.h HAVE_SNPRINTF WINPCAP_HAVE_DEFINES)
winpcap_check_symbol_exists(vsnprintf stdio.h HAVE_VSNPRINTF WINPCAP_HAVE_DEFINES)

# Find libraries containing gethostbyname
set(CMAKE_REQUIRED_DEFINITIONS)
set(lib_with_gethostbyname)
foreach(extra_req_lib "" nsl)
    foreach(library nsl socket resolv)
        if(NOT lib_with_gethostbyname)
            cmake_reset_check_state()
            set(req_libraries ${library})
            if(extra_req_lib)
                list(APPEND req_libraries extra_req_lib)
            endif()
            set(CMAKE_REQUIRED_LIBRARIES ${req_libraries})
            check_library_exists("${library}" gethostbyname "" "GETHOSTBYNAME_IN_${library}_WITH_${extra_req_lib}")
            if(GETHOSTBYNAME_IN_${library})
                set(lib_with_gethostbyname ${req_libraries})
                list(APPEND WINPCAP_LIBRARIES ${lib_with_gethostbyname})
            endif()
        endif()
    endforeach()
endforeach()

cmake_reset_check_state()
check_symbol_exists(getifaddrs ifaddrs.h HAVE_GETIFADDRS)

cmake_reset_check_state()
check_c_source_compiles([[
        #include <sys/param.h>
        #include <sys/file.h>
        #include <sys/ioctl.h>
        #include <sys/socket.h>
        #include <sys/sockio.h>
        int main() {
            ioctl(0, SIOCGLIFCONF, (char *)0);
        }
    ]] HAVE_SIOCGLIFCONF)

check_include_file(unistd.h HAVE_UNISTD_H)
if(NOT HAVE_UNISTD_H)
    list(APPEND WINPCAP_HAVE_DEFINES YY_NO_UNISTD_H)
endif()

find_package(FLEX REQUIRED)
find_package(BISON REQUIRED)

flex_target(wpcap_scanner
    source_subfolder/wpcap/libpcap/scanner.l
    "${CMAKE_CURRENT_BINARY_DIR}/scanner.c"
    COMPILE_FLAGS "--prefix=pcap_"
)
bison_target(wpcap_grammar
    source_subfolder/wpcap/libpcap/grammar.y
    "${CMAKE_CURRENT_BINARY_DIR}/grammar.c"
    COMPILE_FLAGS "-p pcap_"
)

add_library(pcap
    ${CMAKE_CURRENT_LIST_FILE}

    source_subfolder/wpcap/PRJ/WPCAP.DEF
    source_subfolder/wpcap/libpcap/bpf/net/bpf_filter.c
    source_subfolder/wpcap/libpcap/bpf_dump.c
    source_subfolder/wpcap/libpcap/bpf_image.c
    source_subfolder/wpcap/libpcap/etherent.c
    source_subfolder/wpcap/libpcap/gencode.c
    source_subfolder/wpcap/libpcap/inet.c
    source_subfolder/wpcap/libpcap/nametoaddr.c
    source_subfolder/wpcap/libpcap/optimize.c
    source_subfolder/wpcap/libpcap/savefile.c

    source_subfolder/wpcap/libpcap/missing/snprintf.c
        source_subfolder/wpcap/libpcap/pcap-${WINPCAP_CAPTURE_TYPE}.c

    source_subfolder/wpcap/libpcap/pcap.c

    "${CMAKE_CURRENT_BINARY_DIR}/scanner.c"
    "${CMAKE_CURRENT_BINARY_DIR}/grammar.c"
)

target_include_directories(pcap
    PRIVATE
        source_subfolder/wpcap/libpcap
        source_subfolder/wpcap/libpcap/lbl
        source_subfolder/wpcap/libpcap/bpf
        source_subfolder/Common
        source_subfolder/wpcap/../../AirPcap_DevPack/include
)
if(WIN32)
    target_sources(pcap
        PRIVATE
            source_subfolder/wpcap/libpcap/pcap-win32.c
    )
    target_include_directories(pcap
        PRIVATE
            source_subfolder/wpcap/libpcap/Win32/Include
            source_subfolder/wpcap/Win32-Extensions
    )
endif()

set_target_properties(pcap
    PROPERTIES
        DEFINE_SYMBOL LIBPCAP_EXPORTS
)

target_compile_definitions(pcap
    PRIVATE
        LIBPCAP_EXPORTS
        ${WINPCAP_HAVE_DEFINES}
        YY_NEVER_INTERACTIVE
        WPCAP
)

if(WINPCAP_LFS)
    target_compile_definitions(pcap PRIVATE
        _FILE_OFFSET_BITS=64
        _LARGE_FILES
        _LARGEFILE_SOURCE
    )
endif()


if(WINPCAP_REMOTE)
    set(capture_types_supporting_remote bpf linux win32)
    if(WINPCAP_CAPTURE_TYPE IN_LIST capture_types_supporting_remote)
        target_sources(pcap
            PRIVATE
                source_subfolder/wpcap/libpcap/sockutils.c
                source_subfolder/wpcap/libpcap/pcap-new.c
                source_subfolder/wpcap/libpcap/pcap-remote.c
        )
        target_compile_definitions(pcap PRIVATE HAVE_REMOTE)
    else()
        message(FATAL_ERROR "WINPCAP_REMOTE can only be enabled for WINPCAP_CAPTURE_TYPE=${capture_types_supporting_remote}")
    endif()
else()
    if(WIN32)
        message(FATAL_ERROR "Windows requires WINPCAP_REMOTE enabled")
    endif()
endif()

if(WINPCAP_CAPTURE_TYPE MATCHES "^sita$")
elseif(WINPCAP_CAPTURE_TYPE MATCHES "^null")
    target_sources(pcap PRIVATE source_subfolder/wpcap/libpcap/fad-null.c)
else()
    if(HAVE_GETIFADDRS)
        target_sources(pcap PRIVATE source_subfolder/wpcap/libpcap/fad-getad.c)
    elseif(WINPCAP_CAPTURE_TYPE MATCHES "^(dlpi|libdlpi)$")
        target_sources(pcap PRIVATE source_subfolder/wpcap/libpcap/dlpisubs.c)
        if(HAVE_SIOCGLIFCONF)
            target_sources(pcap PRIVATE source_subfolder/wpcap/libpcap/fad-glifc.c)
        else()
            target_sources(pcap PRIVATE source_subfolder/wpcap/libpcap/fad-gifc.c)
        endif()
    else()
        target_sources(pcap PRIVATE source_subfolder/wpcap/libpcap/fad-gifc.c)
    endif()
endif()

if(WINPCAP_CAPTURE_TYPE MATCHES "^sita$")
    target_compile_definitions(pcap PRIVATE SITA=1)
elseif(WINPCAP_CAPTURE_TYPE MATCHES "^dag$")
    find_package(DAG REQUIRED)
    target_link_libraries(pcap PRIVATE DAG::DAG)
    target_compile_definitions(pcap PRIVATE HAVE_DAG_API DAG_ONLY)

    cmake_reset_check_state()
    set(CMAKE_REQUIRED_LIBRARIES "${DAG_LIBRARY}")

    check_function_exists(dag_attach_stream HAVE_DAG_ATTACH_STREAM)
    if(HAVE_DAG_ATTACH_STREAM)
        target_compile_definitions(pcap PRIVATE HAVE_DAG_STREAMS_API)
    endif()

    check_function_exists(dag_get_erf_types HAVE_DAG_GET_ERF_TYPES)
    if(HAVE_DAG_GET_ERF_TYPES)
        target_compile_definitions(pcap PRIVATE HAVE_DAG_GET_ERF_TYPES)
    endif()

    check_function_exists(dag_get_stream_erf_types HAVE_DAG_GET_STREAM_ERF_TYPES)
    if(HAVE_DAG_GET_STREAM_ERF_TYPES)
        target_compile_definitions(pcap PRIVATE HAVE_DAG_GET_STREAM_ERF_TYPES)
    endif()
elseif(WINPCAP_CAPTURE_TYPE MATCHES "^septel")
    find_package(septel REQUIRED)
    target_link_libraries(pcap PRIVATE septel::septel)
    target_compile_definitions(pcap PRIVATE HAVE_DAG_API HAVE_SEPTEL_API SEPTEL_ONLY)
endif()

if(WINPCAP_TURBOCAP)
    set(capture_types_supporting_turbocap linux win32)
    if(WINPCAP_CAPTURE_TYPE IN_LIST capture_types_supporting_turbocap)
        target_sources(pcap
            PRIVATE
                source_subfolder/wpcap/libpcap/pcap-tc.c
        )
        target_compile_definitions(pcap PRIVATE HAVE_TC_API)
        if(WIN32)
            target_sources(pcap
                PRIVATE
                    source_subfolder/wpcap/Win32-Extensions/Win32-Extensions.c
            )
        else()
            find_package(Turbocap REQUIRED)
            find_package(Threads REQUIRED)
            target_link_libraries(pcap
                PRIVATE
                    Threads::Threads
                    Turbocap::Turbocap
            )
        endif()
    else()
        message(FATAL_ERROR "WINPCAP_TURBOCAP can only be enabled for WINPCAP_CAPTURE_TYPE=${capture_types_supporting_turbocap}")
    endif()
else()
    if(WIN32)
        message(FATAL_ERROR "Windows requires WINPCAP_TURBOCAP enabled")
    endif()
endif()

if(MSVC)
    target_compile_definitions(pcap
        PRIVATE
            _CRT_SECURE_NO_WARNINGS
    )
endif()

if(WIN32)
    target_sources(pcap
        PRIVATE
            source_subfolder/wpcap/libpcap/Win32/Src/ffs.c
            source_subfolder/wpcap/libpcap/Win32/Src/getservent.c
    )
    target_link_libraries(pcap
        PRIVATE
            packet ws2_32
    )
    target_compile_definitions(pcap
        PRIVATE
            WIN32
    )
    set_target_properties(pcap
        PROPERTIES
            OUTPUT_NAME wpcap
    )
endif()

if(WINPCAP_IPV6)
    target_compile_definitions(pcap PRIVATE INET6=1)
endif()

if(NOT WINPCAP_PROTOCHAIN)
    target_compile_definitions(pcap PRIVATE NO_PROTOCHAIN)
endif()

if(WINPCAP_BLUETOOTH)
    find_package(bluez REQUIRED)
    target_link_libraries(pcap PRIVATE bluez::bluez)
    target_sources(pcap PRIVATE source_subfolder/wpcap/libpcap/pcap-bt-linux.c)
    target_compile_definitions(pcap
        PRIVATE
            PCAP_SUPPORT_BT
    )
endif()

if(WINPCAP_USB)
    target_sources(pcap PRIVATE source_subfolder/wpcap/libpcap/pcap-usb-linux.c)
    target_compile_definitions(pcap
        PRIVATE
            PCAP_SUPPORT_USB
            "LINUX_USB_MON_DEV=\"${WINPCAP_USB_DEVICE}\""
    )
endif()

install(TARGETS pcap
    ARCHIVE DESTINATION "${cMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
)

# from create_include.bat
file(GLOB WINPCAP_PCAP_HEADERS "source_subfolder/wpcap/libpcap/pcap/*.h")
set(WINPCAP_HEADERS
    source_subfolder/wpcap/libpcap/pcap.h
    source_subfolder/wpcap/libpcap/pcap-bpf.h
    source_subfolder/wpcap/libpcap/pcap-namedb.h
    source_subfolder/wpcap/libpcap/remote-ext.h

    source_subfolder/wpcap/libpcap/pcap-stdinc.h
)
if(WIN32)
    list(APPEND WINPCAP_HEADERS
        source_subfolder/wpcap/Win32-Extensions/Win32-Extensions.h
        source_subfolder/wpcap/libpcap/Win32/Include/bittypes.h
        source_subfolder/wpcap/libpcap/Win32/Include/ip6_misc.h
    )
endif()
if(WINPCAP_BUGGY_TM_SUPPORT)
    list(APPEND WINPCAP_HEADERS
        source_subfolder/packetNtx/driver/bucket_lookup.h
        source_subfolder/packetNtx/driver/count_packets.h
        source_subfolder/packetNtx/driver/memory_t.h
        source_subfolder/packetNtx/driver/normal_lookup.h
        source_subfolder/packetNtx/driver/tcp_session.h
        source_subfolder/packetNtx/driver/time_calls.h
        source_subfolder/packetNtx/driver/tme.h
    )
endif()
list(APPEND WINPCAP_HEADERS
    source_subfolder/Common/Packet32.h
)

install(FILES ${WINPCAP_PCAP_HEADERS}
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/pcap"
)
install(FILES ${WINPCAP_HEADERS}
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)
