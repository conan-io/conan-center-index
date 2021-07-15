cmake_minimum_required(VERSION 3.0)
project(driver C)

include(GNUInstallDirs)

option(PACKET_TME "Enable (buggy) TME extensions")

find_package(WDK REQUIRED)

wdk_add_library(packet
    ${CMAKE_CURRENT_LIST_FILE}

    source_subfolder/packetNtx/driver/Openclos.c
    source_subfolder/packetNtx/driver/Read.c
    source_subfolder/packetNtx/driver/Write.c
    source_subfolder/packetNtx/driver/win_bpf_filter.c
    source_subfolder/packetNtx/driver/NPF.rc
)

if(CMAKE_SIZEOF_VOID_P EQUAL 4)
    target_sources(packet
        PRIVATE
            source_subfolder/packetNtx/jitter.c
    )
endif()

target_compile_definitions(packet
    PRIVATE
        WIN_NT_DRIVER
        WIN32_EXT
        NDIS50  # NDIS30 __NPF_NT4__ for NT 4.0
)

if(PACKET_TME)
    target_sources(packet
        PRIVATE
            source_subfolder/packetNtx/driver/tme.c
            source_subfolder/packetNtx/driver/count_packets.c
            source_subfolder/packetNtx/driver/tcp_session.c
            source_subfolder/packetNtx/driver/functions.c
            source_subfolder/packetNtx/driver/bucket_lookup.c
            source_subfolder/packetNtx/driver/normal_lookup.c
            source_subfolder/packetNtx/driver/win_bpf_filter_init.c
    )
    target_compile_definitions(packet PRIVATE HAVE_BUGGY_TME_SUPPORT)
endif()

install(TARGETS packet
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
)
