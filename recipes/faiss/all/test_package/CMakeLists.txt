cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)


option(WITH_GPU "Building with GPU" ON)
option(WITH_OLD_FAISS "Building with Faiss(<1.8.0) without separated gpu lib" OFF)

set(exe_name "example")
add_executable(${exe_name} src/example.cpp)
if(WITH_GPU)
    find_package(CUDAToolkit REQUIRED)
    target_compile_definitions(${exe_name} PRIVATE WITH_GPU)
endif()


find_package(OpenMP REQUIRED)
find_package(faiss CONFIG REQUIRED)
if(faiss_VERSION_STRING STREQUAL "1.7.4")
    set(WITH_OLD_FAISS ON)
endif()

set(faiss_comp faiss)
if(TARGET faiss::faiss_avx512 AND OFF) # avx512 is not common
    set(faiss_comp faiss_avx512)
elseif(TARGET faiss::faiss_avx2)
    set(faiss_comp faiss_avx2)
endif()
message(STATUS "${exe_name}: using ${faiss_comp}(OLD=${WITH_OLD_FAISS}) WITH_GPU=${WITH_GPU}")

# TODO: Because conan-center-index has no OpenMP/system and CUDAToolkit/system
# yet, consumer of faiss must express below dependencies by itself:
if(WITH_OLD_FAISS)
    # faiss_avx2 +-> OpenMP
    #            | (optional: WITH_GPU)
    #            +-> cublas
    #            |     |
    #            |     v
    #            +-> cudart
    target_link_libraries(${exe_name} faiss::${faiss_comp})
    target_link_libraries(faiss::${faiss_comp} INTERFACE OpenMP::OpenMP_CXX)
    if(WITH_GPU)
        target_link_libraries(faiss::${faiss_comp} INTERFACE CUDA::cublas CUDA::cudart)
    endif()
else()
    # faiss v1.8.0 extracts gpu as a separate library
    #   faiss_avx2_gpu +-> faiss_avx2 -> OpenMP
    #                  | (optional: WITH_GPU)
    #                  +-> cublas
    #                  |     |
    #                  |     v
    #                  +-> cudart
    target_link_libraries(faiss::${faiss_comp} INTERFACE OpenMP::OpenMP_CXX)
    if(WITH_GPU)
        target_link_libraries(${exe_name} faiss::${faiss_comp}_gpu)
        target_link_libraries(faiss::${faiss_comp}_gpu INTERFACE CUDA::cublas CUDA::cudart)
    else()
        target_link_libraries(${exe_name} faiss::${faiss_comp})
    endif()
endif()
