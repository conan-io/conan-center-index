cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

option(WITH_GMP "With GMP" OFF)

add_library(libbliss
    source_subfolder/bliss_C.cc
    source_subfolder/defs.cc
    source_subfolder/Doxyfile
    source_subfolder/graph.cc
    source_subfolder/heap.cc
    source_subfolder/orbit.cc
    source_subfolder/partition.cc
    source_subfolder/timer.cc
    source_subfolder/uintseqhash.cc
    source_subfolder/utils.cc
)
set_property(TARGET libbliss PROPERTY OUTPUT_NAME bliss)
target_link_libraries(libbliss PUBLIC ${CONAN_LIBS})
if(WITH_GMP)
    target_compile_definitions(libbliss PUBLIC BLISS_USE_GMP)
endif()
if(WIN32 AND BUILD_SHARED_LIBS)
    set_property(TARGET libbliss PROPERTY WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()


add_executable(bliss
    source_subfolder/bliss.cc
)
target_link_libraries(bliss PRIVATE libbliss)

install(TARGETS libbliss bliss
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)
install(FILES
        source_subfolder/bliss_C.h
        source_subfolder/heap.hh
        source_subfolder/kqueue.hh
        source_subfolder/kstack.hh
        source_subfolder/utils.hh
        source_subfolder/bignum.hh
        source_subfolder/graph.hh
        source_subfolder/defs.hh
        source_subfolder/timer.hh
        source_subfolder/uintseqhash.hh
        source_subfolder/partition.hh
        source_subfolder/orbit.hh
    DESTINATION include/bliss
)
