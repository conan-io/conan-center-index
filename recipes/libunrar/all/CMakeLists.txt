cmake_minimum_required (VERSION 3.7...3.15)

project (unrar CXX)

option(BUILD_SHARED_LIBS  "Enable shared library" OFF)
set(CMAKE_CXX_FLAGS "-march=native -O2 -std=c++11 -Wno-logical-op-parentheses -Wno-switch -Wno-dangling-else")
add_compile_definitions(_FILE_OFFSET_BITS=64 _LARGEFILE_SOURCE RAR_SMP RARDLL)

set(unrar_lib
        filestr.cpp
        scantree.cpp
        dll.cpp
        qopen.cpp
)

set(unrar_src
        rar.cpp
        strlist.cpp
        strfn.cpp
        pathfn.cpp
        smallfn.cpp
        global.cpp
        file.cpp
        filefn.cpp
        filcreat.cpp
	    archive.cpp
        arcread.cpp
        unicode.cpp
        system.cpp
        crypt.cpp
        crc.cpp
        rawread.cpp
        encname.cpp
	    resource.cpp
        match.cpp
        timefn.cpp
        rdwrfn.cpp
        consio.cpp
        options.cpp
        errhnd.cpp
        rarvm.cpp
        secpassword.cpp
	    rijndael.cpp
        getbits.cpp
        sha1.cpp
        sha256.cpp
        blake2s.cpp
        hash.cpp
        extinfo.cpp
        extract.cpp
        volume.cpp
	    list.cpp
        find.cpp
        unpack.cpp
        headers.cpp
        threadpool.cpp
        rs16.cpp
        cmddata.cpp
        ui.cpp
)

if (BUILD_SHARED_LIBS)
    add_library(${PROJECT_NAME} SHARED ${unrar_src} ${unrar_lib})
else ()
    add_library(${PROJECT_NAME} STATIC ${unrar_src} ${unrar_lib})
endif ()

set(CMAKE_LINK_LIBRARY_FLAG "-pthread")

#common header
file(GLOB unrar_header "*.hpp")

install(FILES ${unrar_header}
        DESTINATION ${CMAKE_INSTALL_PREFIX}/include/unrar)

install(TARGETS  ${PROJECT_NAME}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
