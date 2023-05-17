cmake_minimum_required(VERSION 3.15)
project(crunch LANGUAGES CXX)

include(GNUInstallDirs)

include_directories(
    ${CRUNCH_FOLDER}/inc
    ${CRUNCH_FOLDER}/crnlib
)

# Crnlib

set(CRNLIB_SRCS
    ${CRUNCH_FOLDER}/crnlib/crn_arealist.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_assert.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_checksum.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_colorized_console.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_command_line_params.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_comp.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_console.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_core.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_data_stream.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dds_comp.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_decomp.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt1.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt5a.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt_endpoint_refiner.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt_fast.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt_hc.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt_hc_common.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt_image.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dynamic_string.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_etc.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_file_utils.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_find_files.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_hash.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_hash_map.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_huffman_codes.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_image_utils.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_jpgd.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_jpge.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_ktx_texture.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_lzma_codec.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_math.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_mem.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_miniz.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_mipmapped_texture.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_pixel_format.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_platform.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_prefix_coding.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_qdxt1.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_qdxt5.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_rand.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_resample_filters.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_resampler.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_rg_etc1.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_ryg_dxt.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_sparse_bit_array.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_stb_image.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_strutils.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_symbol_codec.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_texture_comp.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_texture_conversion.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_texture_file_types.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_threaded_resampler.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_timer.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_utils.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_value.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_vector.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_zeng.cpp
    ${CRUNCH_FOLDER}/crnlib/crnlib.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_7zBuf.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_7zBuf2.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_7zFile.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_7zStream.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_Alloc.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_Bcj2.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_Bra.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_Bra86.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_BraIA64.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_LzFind.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_LzmaDec.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_LzmaEnc.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_LzmaLib.cpp
)

if(WIN32)
    list(APPEND CRNLIB_SRCS
        ${CRUNCH_FOLDER}/crnlib/lzma_LzFindMt.cpp
        ${CRUNCH_FOLDER}/crnlib/lzma_Threads.cpp
        ${CRUNCH_FOLDER}/crnlib/crn_threading_win32.cpp
    )
else()
    list(APPEND CRNLIB_SRCS
        ${CRUNCH_FOLDER}/crnlib/crn_threading_pthreads.cpp
    )
endif()

add_library(crnlib ${CRNLIB_SRCS})
if(NOT WIN32)
    find_package(Threads REQUIRED)
    target_link_libraries(crnlib PUBLIC Threads::Threads)
endif()

# Crunch

add_executable(crunch
    ${CRUNCH_FOLDER}/crunch/corpus_gen.cpp
    ${CRUNCH_FOLDER}/crunch/corpus_test.cpp
    ${CRUNCH_FOLDER}/crunch/crunch.cpp
)
target_link_libraries(crunch PRIVATE crnlib)

# Install

install(TARGETS crnlib crunch
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    BUNDLE DESTINATION ${CMAKE_INSTALL_BINDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
file(GLOB HDRS ${CRUNCH_FOLDER}/inc/*.h)
install(FILES ${HDRS} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
