cmake_minimum_required(VERSION 2.8.12)
project(crunch)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(CRUNCH_FOLDER ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder)

include_directories(
    ${CRUNCH_FOLDER}/inc
    ${CRUNCH_FOLDER}/crnlib
)

# Crnlib

set(CRNLIB_SRCS
    ${CRUNCH_FOLDER}/crnlib/crn_arealist.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_arealist.h
    ${CRUNCH_FOLDER}/crnlib/crn_assert.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_assert.h
    ${CRUNCH_FOLDER}/crnlib/crn_buffer_stream.h
    ${CRUNCH_FOLDER}/crnlib/crn_cfile_stream.h
    ${CRUNCH_FOLDER}/crnlib/crn_checksum.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_checksum.h
    ${CRUNCH_FOLDER}/crnlib/crn_clusterizer.h
    ${CRUNCH_FOLDER}/crnlib/crn_color.h
    ${CRUNCH_FOLDER}/crnlib/crn_colorized_console.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_colorized_console.h
    ${CRUNCH_FOLDER}/crnlib/crn_command_line_params.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_command_line_params.h
    ${CRUNCH_FOLDER}/crnlib/crn_comp.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_comp.h
    ${CRUNCH_FOLDER}/crnlib/crn_console.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_console.h
    ${CRUNCH_FOLDER}/crnlib/crn_core.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_core.h
    ${CRUNCH_FOLDER}/crnlib/crn_data_stream.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_data_stream.h
    ${CRUNCH_FOLDER}/crnlib/crn_data_stream_serializer.h
    ${CRUNCH_FOLDER}/crnlib/crn_dds_comp.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dds_comp.h
    ${CRUNCH_FOLDER}/crnlib/crn_decomp.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt.h
    ${CRUNCH_FOLDER}/crnlib/crn_dxt1.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt1.h
    ${CRUNCH_FOLDER}/crnlib/crn_dxt5a.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt5a.h
    ${CRUNCH_FOLDER}/crnlib/crn_dxt_endpoint_refiner.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt_endpoint_refiner.h
    ${CRUNCH_FOLDER}/crnlib/crn_dxt_fast.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt_fast.h
    ${CRUNCH_FOLDER}/crnlib/crn_dxt_hc.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt_hc.h
    ${CRUNCH_FOLDER}/crnlib/crn_dxt_hc_common.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt_hc_common.h
    ${CRUNCH_FOLDER}/crnlib/crn_dxt_image.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dxt_image.h
    ${CRUNCH_FOLDER}/crnlib/crn_dynamic_stream.h
    ${CRUNCH_FOLDER}/crnlib/crn_dynamic_string.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_dynamic_string.h
    ${CRUNCH_FOLDER}/crnlib/crn_etc.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_etc.h
    ${CRUNCH_FOLDER}/crnlib/crn_file_utils.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_file_utils.h
    ${CRUNCH_FOLDER}/crnlib/crn_find_files.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_find_files.h
    ${CRUNCH_FOLDER}/crnlib/crn_hash.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_hash.h
    ${CRUNCH_FOLDER}/crnlib/crn_hash_map.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_hash_map.h
    ${CRUNCH_FOLDER}/crnlib/crn_helpers.h
    ${CRUNCH_FOLDER}/crnlib/crn_huffman_codes.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_huffman_codes.h
    ${CRUNCH_FOLDER}/crnlib/crn_image.h
    ${CRUNCH_FOLDER}/crnlib/crn_image_utils.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_image_utils.h
    ${CRUNCH_FOLDER}/crnlib/crn_intersect.h
    ${CRUNCH_FOLDER}/crnlib/crn_jpgd.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_jpgd.h
    ${CRUNCH_FOLDER}/crnlib/crn_jpge.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_jpge.h
    ${CRUNCH_FOLDER}/crnlib/crn_ktx_texture.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_ktx_texture.h
    ${CRUNCH_FOLDER}/crnlib/crn_lzma_codec.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_lzma_codec.h
    ${CRUNCH_FOLDER}/crnlib/crn_math.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_math.h
    ${CRUNCH_FOLDER}/crnlib/crn_matrix.h
    ${CRUNCH_FOLDER}/crnlib/crn_mem.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_mem.h
    ${CRUNCH_FOLDER}/crnlib/crn_miniz.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_miniz.h
    ${CRUNCH_FOLDER}/crnlib/crn_mipmapped_texture.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_mipmapped_texture.h
    ${CRUNCH_FOLDER}/crnlib/crn_packed_uint.h
    ${CRUNCH_FOLDER}/crnlib/crn_pixel_format.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_pixel_format.h
    ${CRUNCH_FOLDER}/crnlib/crn_platform.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_platform.h
    ${CRUNCH_FOLDER}/crnlib/crn_prefix_coding.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_prefix_coding.h
    ${CRUNCH_FOLDER}/crnlib/crn_qdxt1.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_qdxt1.h
    ${CRUNCH_FOLDER}/crnlib/crn_qdxt5.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_qdxt5.h
    ${CRUNCH_FOLDER}/crnlib/crn_rand.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_rand.h
    ${CRUNCH_FOLDER}/crnlib/crn_ray.h
    ${CRUNCH_FOLDER}/crnlib/crn_rect.h
    ${CRUNCH_FOLDER}/crnlib/crn_resample_filters.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_resample_filters.h
    ${CRUNCH_FOLDER}/crnlib/crn_resampler.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_resampler.h
    ${CRUNCH_FOLDER}/crnlib/crn_rg_etc1.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_rg_etc1.h
    ${CRUNCH_FOLDER}/crnlib/crn_ryg_dxt.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_ryg_dxt.hpp
    ${CRUNCH_FOLDER}/crnlib/crn_ryg_types.hpp
    ${CRUNCH_FOLDER}/crnlib/crn_sparse_array.h
    ${CRUNCH_FOLDER}/crnlib/crn_sparse_bit_array.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_sparse_bit_array.h
    ${CRUNCH_FOLDER}/crnlib/crn_stb_image.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_strutils.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_strutils.h
    ${CRUNCH_FOLDER}/crnlib/crn_symbol_codec.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_symbol_codec.h
    ${CRUNCH_FOLDER}/crnlib/crn_texture_comp.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_texture_comp.h
    ${CRUNCH_FOLDER}/crnlib/crn_texture_conversion.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_texture_conversion.h
    ${CRUNCH_FOLDER}/crnlib/crn_texture_file_types.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_texture_file_types.h
    ${CRUNCH_FOLDER}/crnlib/crn_threaded_clusterizer.h
    ${CRUNCH_FOLDER}/crnlib/crn_threaded_resampler.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_threaded_resampler.h
    ${CRUNCH_FOLDER}/crnlib/crn_threading.h
    ${CRUNCH_FOLDER}/crnlib/crn_threading_null.h
    ${CRUNCH_FOLDER}/crnlib/crn_timer.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_timer.h
    ${CRUNCH_FOLDER}/crnlib/crn_traits.h
    ${CRUNCH_FOLDER}/crnlib/crn_tree_clusterizer.h
    ${CRUNCH_FOLDER}/crnlib/crn_types.h
    ${CRUNCH_FOLDER}/crnlib/crn_utils.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_utils.h
    ${CRUNCH_FOLDER}/crnlib/crn_value.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_value.h
    ${CRUNCH_FOLDER}/crnlib/crn_vec.h
    ${CRUNCH_FOLDER}/crnlib/crn_vec_interval.h
    ${CRUNCH_FOLDER}/crnlib/crn_vector.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_vector.h
    ${CRUNCH_FOLDER}/crnlib/crn_vector2d.h
    ${CRUNCH_FOLDER}/crnlib/crn_winhdr.h
    ${CRUNCH_FOLDER}/crnlib/crn_zeng.cpp
    ${CRUNCH_FOLDER}/crnlib/crn_zeng.h
    ${CRUNCH_FOLDER}/crnlib/crnlib.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_7zBuf.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_7zBuf.h
    ${CRUNCH_FOLDER}/crnlib/lzma_7zBuf2.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_7zCrc.h
    ${CRUNCH_FOLDER}/crnlib/lzma_7zFile.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_7zFile.h
    ${CRUNCH_FOLDER}/crnlib/lzma_7zStream.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_7zVersion.h
    ${CRUNCH_FOLDER}/crnlib/lzma_Alloc.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_Alloc.h
    ${CRUNCH_FOLDER}/crnlib/lzma_Bcj2.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_Bcj2.h
    ${CRUNCH_FOLDER}/crnlib/lzma_Bra.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_Bra.h
    ${CRUNCH_FOLDER}/crnlib/lzma_Bra86.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_BraIA64.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_CpuArch.h
    ${CRUNCH_FOLDER}/crnlib/lzma_LzFind.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_LzFind.h
    ${CRUNCH_FOLDER}/crnlib/lzma_LzHash.h
    ${CRUNCH_FOLDER}/crnlib/lzma_LzmaDec.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_LzmaDec.h
    ${CRUNCH_FOLDER}/crnlib/lzma_LzmaEnc.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_LzmaEnc.h
    ${CRUNCH_FOLDER}/crnlib/lzma_LzmaLib.cpp
    ${CRUNCH_FOLDER}/crnlib/lzma_LzmaLib.h
    ${CRUNCH_FOLDER}/crnlib/lzma_MyVersion.h
    ${CRUNCH_FOLDER}/crnlib/lzma_Types.h
    ${CRUNCH_FOLDER}/crnlib/../inc/crn_decomp.h
    ${CRUNCH_FOLDER}/crnlib/../inc/crnlib.h
    ${CRUNCH_FOLDER}/crnlib/../inc/dds_defs.h
)

if(WIN32)
    list(APPEND CRNLIB_SRCS
        ${CRUNCH_FOLDER}/crnlib/lzma_LzFindMt.cpp
        ${CRUNCH_FOLDER}/crnlib/lzma_LzFindMt.h
        ${CRUNCH_FOLDER}/crnlib/lzma_Threads.cpp
        ${CRUNCH_FOLDER}/crnlib/lzma_Threads.h
        ${CRUNCH_FOLDER}/crnlib/crn_threading_win32.cpp
        ${CRUNCH_FOLDER}/crnlib/crn_threading_win32.h
    )
else(WIN32)
    list(APPEND CRNLIB_SRCS
        ${CRUNCH_FOLDER}/crnlib/crn_threading_pthreads.h
        ${CRUNCH_FOLDER}/crnlib/crn_threading_pthreads.cpp
    )
endif()

add_library(crnlib ${CRNLIB_SRCS})

if(NOT WIN32)
    find_package(Threads REQUIRED)

    if(${CMAKE_VERSION} VERSION_LESS "3.0")
        target_link_libraries(crnlib PUBLIC ${CMAKE_THREAD_LIBS_INIT})
    else()
        target_link_libraries(crnlib PUBLIC Threads::Threads)
    endif()
endif()

# Crunch

set(CRUNCH_SRCS
    ${CRUNCH_FOLDER}/crunch/corpus_gen.cpp
    ${CRUNCH_FOLDER}/crunch/corpus_gen.h
    ${CRUNCH_FOLDER}/crunch/corpus_test.cpp
    ${CRUNCH_FOLDER}/crunch/corpus_test.h
    ${CRUNCH_FOLDER}/crunch/crunch.cpp
)

add_executable(crunch ${CRUNCH_SRCS})
target_link_libraries(crunch PUBLIC crnlib)

# Install

install(TARGETS crnlib crunch RUNTIME ARCHIVE LIBRARY)
file(GLOB HDRS ${CRUNCH_FOLDER}/inc/*.h)
install(FILES ${HDRS} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
