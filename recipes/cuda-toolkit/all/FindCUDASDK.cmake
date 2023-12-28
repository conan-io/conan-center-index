cmake_minimum_required(VERSION 3.0)

# parse nvcc --version
function(_find_nvcc_read_nvcc_version nvcc_program cuda_version is_valid)
  set(${is_valid}
      FALSE
      PARENT_SCOPE)
  if(NOT EXISTS "${nvcc_program}")
    return()
  endif()
  execute_process(COMMAND ${nvcc_program} "--version"
                  OUTPUT_VARIABLE version_info)
  if("${version_info}" MATCHES [=[ V([0-9]+)\.([0-9]+)\.([0-9]+)]=])
    set(${cuda_version}
        "${CMAKE_MATCH_1}.${CMAKE_MATCH_2}.${CMAKE_MATCH_3}"
        PARENT_SCOPE)
    set(${is_valid}
        TRUE
        PARENT_SCOPE)
  endif()
endfunction()

# read and parse version.txt file
function(_find_nvcc_read_file_version_txt version_file cuda_version is_valid)
  set(${is_valid}
      FALSE
      PARENT_SCOPE)
  if(NOT EXISTS "${version_file}")
    return()
  endif()
  file(READ "${version_file}" version_info)
  if("${version_info}" MATCHES [=[CUDA Version ([0-9]+)\.([0-9]+)\.([0-9]+)]=])
    set(${cuda_version}
        "${CMAKE_MATCH_1}.${CMAKE_MATCH_2}.${CMAKE_MATCH_3}"
        PARENT_SCOPE)
    set(${is_valid}
        TRUE
        PARENT_SCOPE)
  endif()
endfunction()

# read and parse version.json
# \TODO use string(JSON ... ) if cmake version is >=3.19
function(_find_nvcc_read_file_version_json version_file cuda_version is_valid)
  set(${is_valid}
      FALSE
      PARENT_SCOPE)
  if(NOT EXISTS "${version_file}")
    return()
  endif()
  file(READ "${version_file}" version_info)
  # read file line by line
  string(REGEX REPLACE ";" "\\\\;" version_lines "${version_info}")
  string(REGEX REPLACE "\n" ";" version_lines "${version_info}")
  string(REGEX REPLACE ";;" ";" version_lines "${version_lines}")
  list(LENGTH version_lines lines_count)
  math(EXPR lines_count "${lines_count}-1")
  foreach(index RANGE 0 ${lines_count} 1)
    list(GET version_lines ${index} version_line)
    if(version_line MATCHES [=[\"CUDA SDK\"]=])
      math(EXPR index_test "${index}-1")
      if(index_test GREATER_EQUAL 0)
        list(GET version_lines ${index_test} line_test)
        if(line_test MATCHES [=[\"([0-9]+)\.([0-9]+)\.([0-9]+)\"]=])
          set(${cuda_version}
              "${CMAKE_MATCH_1}.${CMAKE_MATCH_2}.${CMAKE_MATCH_3}"
              PARENT_SCOPE)
          set(${is_valid}
              TRUE
              PARENT_SCOPE)
        endif()
      endif()
      math(EXPR index_test "${index}+1")
      if(index_test LESS_EQUAL lines_count)
        list(GET version_lines ${index_test} line_test)
        if(line_test MATCHES [=[\"([0-9]+)\.([0-9]+)\.([0-9]+)\"]=])
          set(${cuda_version}
              "${CMAKE_MATCH_1}.${CMAKE_MATCH_2}.${CMAKE_MATCH_3}"
              PARENT_SCOPE)
          set(${is_valid}
              TRUE
              PARENT_SCOPE)
        endif()
      endif()
      break()
    endif()
  endforeach()
endfunction()

# parse sdk version for visual studio integration version
function(_find_nvcc_toolbox_version custom_target_path cudasdk_version is_valid)
  set(${is_valid}
      FALSE
      PARENT_SCOPE)
  if(NOT EXISTS "${custom_target_path}")
    return()
  endif()
  string(REPLACE "\\" "/" custom_target_path "${custom_target_path}")
  file(
    GLOB file_list
    LIST_DIRECTORIES False
    "${custom_target_path}/CUDA *.props")
  list(LENGTH file_list file_count)
  if(file_count GREATER 0)
    list(GET file_list 0 file_fullpath)
    string(REPLACE "${custom_target_path}" "" file_fullpath "${file_fullpath}")
    if("${file_fullpath}" MATCHES [=[CUDA ([0-9]+)(\.[0-9]+)?(\.[0-9]+)?]=])
      if(CMAKE_MATCH_COUNT EQUAL 1)
        set(${cudasdk_version}
            "${CMAKE_MATCH_1}"
            PARENT_SCOPE)
        set(${is_valid}
            TRUE
            PARENT_SCOPE)
      elseif(CMAKE_MATCH_COUNT EQUAL 2)
        set(${cudasdk_version}
            "${CMAKE_MATCH_1}${CMAKE_MATCH_2}"
            PARENT_SCOPE)
        set(${is_valid}
            TRUE
            PARENT_SCOPE)
      elseif(CMAKE_MATCH_COUNT EQUAL 3)
        set(${cudasdk_version}
            "${CMAKE_MATCH_1}${CMAKE_MATCH_2}${CMAKE_MATCH_3}"
            PARENT_SCOPE)
        set(${is_valid}
            TRUE
            PARENT_SCOPE)
      endif()
    endif()
  endif()
endfunction()

# uruchamia ustawienie wartosci jsona pre version 11 use version.txt file 11 or
# above use version.json otherwise use nvcc --version to get current version
function(_find_nvcc cuda_path)
  set(cuda_version "")
  set(nvcc_dir "")
  set(int_dir "")
  if(EXISTS "${cuda_path}/nvcc")
    set(nvcc_dir "/nvcc")
    set(int_dir "/CUDAVisualStudioIntegration")
  endif()
  _find_nvcc_read_file_version_json("${cuda_path}${nvcc_dir}/version.json"
                                    cuda_version is_valid)
  _find_nvcc_read_file_version_txt("${cuda_path}${nvcc_dir}/version.txt"
                                   cuda_version is_valid)
  if(NOT cuda_version)
    find_program(
      nvcc_program nvcc
      PATHS "${cuda_path}${nvcc_dir}/bin" NO_CACHE
      NO_DEFAULT_PATH NO_PACKAGE_ROOT_PATH NO_CMAKE_PATH
      NO_CMAKE_ENVIRONMENT_PATH NO_SYSTEM_ENVIRONMENT_PATH NO_CMAKE_SYSTEM_PATH)
    _find_nvcc_read_nvcc_version("${nvcc_program}" cuda_version is_valid)
  endif()
  unset(cudasdk_version)
  _find_nvcc_toolbox_version(
    "${cuda_path}${int_dir}/extras/visual_studio_integration/MSBuildExtensions"
    cudasdk_version is_valid)
  if(cuda_version)

    if(cudasdk_version)
      set(CMAKE_VS_PLATFORM_TOOLSET_CUDA
          "${cudasdk_version}"
          CACHE INTERNAL "CUDA_VERSION" FORCE)
    else()
      set(CMAKE_VS_PLATFORM_TOOLSET_CUDA
          "${cuda_version}"
          CACHE INTERNAL "CUDA_VERSION" FORCE)
    endif()
    # for some reason this need to be set (value exists in format XX.Y during
    # startup under MSVS)
    set(CMAKE_VS_PLATFORM_TOOLSET_CUDA
        "${CMAKE_VS_PLATFORM_TOOLSET_CUDA}"
        PARENT_SCOPE)
    set(CMAKE_VS_PLATFORM_TOOLSET_CUDA_CUSTOM_DIR
        "${cuda_path}/"
        CACHE INTERNAL "CUDA_CUSTOM_DIR" FORCE)
    set(CUDAToolset_ROOT
        "${cuda_path}${nvcc_dir}/"
        CACHE INTERNAL "CUDA_CUSTOM_DIR" FORCE)

    # this is undefined behaviour for CMAKE
    if(NOT CMAKE_GENERATOR_TOOLSET)
      set(CMAKE_GENERATOR_TOOLSET
          "cuda=${cuda_path}"
          CACHE INTERNAL "Name of generator toolset." FORCE)
    elseif(NOT "${CMAKE_GENERATOR_TOOLSET}" MATCHES [=[cuda=]=])
      set(CMAKE_GENERATOR_TOOLSET
          "${CMAKE_GENERATOR_TOOLSET},cuda=${cuda_path}"
          CACHE INTERNAL "Name of generator toolset." FORCE)
    else()
      string(REGEX REPLACE "(,cuda=[^,]+)|(cuda=[^,]+,)|(cuda=[^,]+)" "" OLDGENEROTOR "${CMAKE_GENERATOR_TOOLSET}")
      if ("${OLDGENERATOR}" STREQUAL "")
        set(CMAKE_GENERATOR_TOOLSET
            "cuda=${cuda_path}"
            CACHE INTERNAL "Name of generator toolset." FORCE)
      else()
        set(CMAKE_GENERATOR_TOOLSET
            "${OLDGENEROTOR},cuda=${cuda_path}"
            CACHE INTERNAL "Name of generator toolset." FORCE)
      endif()
    endif()
    set(CUDASDK_FOUND
        TRUE
        PARENT_SCOPE)
    set(CUDASDK_VERSION
        "${CMAKE_VS_PLATFORM_TOOLSET_CUDA}"
        PARENT_SCOPE)

    set(CUDA_VERSION "${CMAKE_VS_PLATFORM_TOOLSET_CUDA}")
    include(FindCUDA/select_compute_arch)
    string(REPLACE "." "" nvcc_arch "${CUDA_COMMON_GPU_ARCHITECTURES}")
    string(REPLACE "+PTX" "" nvcc_arch "${nvcc_arch}")
    list(REMOVE_DUPLICATES nvcc_arch)
    if (NOT DEFINED CMAKE_CUDA_ARCHITECTURES)
        if (DEFINED ENV{CUDAARCHS})
            set(CMAKE_CUDA_ARCHITECTURES
                "$ENV{CUDAARCHS}"
                CACHE STRING "CUDA Architectures" FORCE)
        else()
            set(CMAKE_CUDA_ARCHITECTURES
                "${nvcc_arch}"
                 CACHE STRING "CUDA Architectures" FORCE)
        endif()
    else()
        get_property(cache_type CACHE CMAKE_CUDA_ARCHITECTURES PROPERTY TYPE)
        if (NOT cache_type)
            set(CMAKE_CUDA_ARCHITECTURES "${CMAKE_CUDA_ARCHITECTURES}" CACHE STRING "CUDA Architectures")
        endif()
    endif()
  else()
    set(CUDASDK_FOUND
        FALSE
        PARENT_SCOPE)
  endif()
endfunction()

function(_cudasdk_make_targets)
  set(cuda_targets cudart cudart_static cuda_driver cublas cublas_static
    cublasLt cublasLt_static cuFile cuFile_static cuFile_rdma cuFile_rdma_static
    cufft cufftw cufft_static cufft_static_nocallback cufftw_static curand curand_static cusolver cusolver_static
    cusparse cusparse_static cupti cupti_static nppc nppc_static nppial nppial_static nppicc nppicc_static nppicom nppicom_static
    nppidei nppidei_static nppif nppif_static nppig nppig_static nppim nppim_static nppist nppist_static nppisu
    nppisu_static nppitc nppitc_static npps npps_static nvblas nvgraph nvgraph_static nvjpeg nvjpeg_static nvptxcompiler
    nvrtc nvml nvToolsExt nvtx3 OpenCL culibos)
  foreach (cuda_target IN LISTS cuda_targets)
    if (NOT TARGET CUDA::${cuda_target})
      continue()
    endif()
    add_library(CUDASDK::${cuda_target} ALIAS CUDA::${cuda_target})
  endforeach()
endfunction()

_find_nvcc("${CMAKE_CURRENT_LIST_DIR}")
if(NOT TARGET CUDASDK::CUDASDK)
  add_library(CUDASDK::CUDASDK INTERFACE IMPORTED)
endif()
# required to be before find_package(CUDAToolkit)
enable_language(CUDA)
find_package(CUDAToolkit REQUIRED)
foreach(variable CMAKE_CUDA_FLAGS CMAKE_CUDA_FLAGS_RELEASE CMAKE_CUDA_FLAGS_DEBUG CMAKE_CUDA_FLAGS_RELWITHDEBINFO CMAKE_CUDA_FLAGS_MINSIZEREL)
	if(NOT "${${variable}}" STREQUAL "")
		string(REPLACE "/MTd" "" ${variable} "${${variable}}")
		string(REPLACE "/MDd" "" ${variable} "${${variable}}")
		string(REPLACE "/MT" "" ${variable} "${${variable}}")
		string(REPLACE "/MD" "" ${variable} "${${variable}}")
		string(REPLACE "-MTd" "" ${variable} "${${variable}}")
		string(REPLACE "-MDd" "" ${variable} "${${variable}}")
		string(REPLACE "-MT" "" ${variable} "${${variable}}")
		string(REPLACE "-MD" "" ${variable} "${${variable}}")
	endif()
endforeach()

_cudasdk_make_targets()
