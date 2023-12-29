cmake_minimum_required(VERSION 3.9)

# parse nvcc --version
#[=======================================================================[.rst:
_cudatoolkit_toolchain_version_nvcc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Parse CUDA version from `nvcc --version`
#]=======================================================================]
function(_cudatoolkit_toolchain_version_nvcc toolkit_version nvcc_executable)
  if(NOT EXISTS "${nvcc_executable}")
    set(${toolkit_version} "${toolkit_version}-NOTFOUND" PARENT_SCOPE)
    return()
  endif()
  execute_process(COMMAND ${nvcc_executable} "--version"
                  OUTPUT_VARIABLE version_info)
  if("${version_info}" MATCHES [=[ V([0-9]+)\.([0-9]+)\.([0-9]+)]=])
    set(${toolkit_version}
        "${CMAKE_MATCH_1}.${CMAKE_MATCH_2}.${CMAKE_MATCH_3}"
        PARENT_SCOPE)
  else()
    set(${toolkit_version} "${toolkit_version}-NOTFOUND" PARENT_SCOPE)
  endif()
endfunction()

#[=======================================================================[.rst:
_cudatoolkit_toolchain_version_txt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CUDA Toolkit version <11 would contain version.txt file that contains CUDA Version
#]=======================================================================]
function(_cudatoolkit_toolchain_version_txt toolkit_version toolkit_path)
  set(version_file "${toolkit_path}/version.txt")
  if(NOT EXISTS "${version_file}")
    set(${toolkit_version} "${toolkit_version}-NOTFOUND" PARENT_SCOPE)
    return()
  endif()
  file(READ "${version_file}" version_info)
  if("${version_info}" MATCHES [=[CUDA Version ([0-9]+)\.([0-9]+)\.([0-9]+)]=])
    set(${cuda_version}
        "${CMAKE_MATCH_1}.${CMAKE_MATCH_2}.${CMAKE_MATCH_3}"
        PARENT_SCOPE)
  else()
    set(${toolkit_version} "${toolkit_version}-NOTFOUND" PARENT_SCOPE)
  endif()
endfunction()

#[=======================================================================[.rst:
_cudatoolkit_toolchain_version_json
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CUDA Toolkit version >=11 contains file version.json that stores package versions.

Functions read whole file and process it line by line (json is formated as new line for each field), it
search for "CUDA SDK" and checks line before and line after for valid version semver.
#]=======================================================================]
function(_cudatoolkit_toolchain_version_json toolkit_version toolkit_path)
  set(version_file "${toolkit_path}/version.json")
  if(NOT EXISTS "${version_file}")
    message(STATUS "version file nat found")
    set(${toolkit_version} "${toolkit_version}-NOTFOUND" PARENT_SCOPE)
    return()
  endif()
  file(READ "${version_file}" version_info)
  # read file line by line
  string(REGEX REPLACE ";" "\\\\;" version_lines "${version_info}")
  string(REGEX REPLACE "\n" ";" version_lines "${version_info}")
  string(REGEX REPLACE ";;" ";" version_lines "${version_lines}")
  list(LENGTH version_lines lines_count)
  math(EXPR lines_count "${lines_count}-1")
  set(found_version "${toolkit_version}-NOTFOUND")
  foreach(index RANGE 0 ${lines_count} 1)
    list(GET version_lines ${index} version_line)
    if(version_line MATCHES [=[\"CUDA SDK\"]=])
      math(EXPR index_test "${index}-1")
      if(index_test GREATER_EQUAL 0)
        list(GET version_lines ${index_test} line_test)
        if(line_test MATCHES [=[\"([0-9]+)\.([0-9]+)\.([0-9]+)\"]=])
          set(found_version "${CMAKE_MATCH_1}.${CMAKE_MATCH_2}.${CMAKE_MATCH_3}")
          break()
        endif()
      endif()
      math(EXPR index_test "${index}+1")
      if(index_test LESS_EQUAL lines_count)
        list(GET version_lines ${index_test} line_test)
        if(line_test MATCHES [=[\"([0-9]+)\.([0-9]+)\.([0-9]+)\"]=])
          set(found_version "${CMAKE_MATCH_1}.${CMAKE_MATCH_2}.${CMAKE_MATCH_3}")
          break()
        endif()
      endif()
      break()
    endif()
  endforeach()
  set(${toolkit_version} "${found_version}" PARENT_SCOPE)
endfunction()


#[=======================================================================[.rst:
_cudatoolkit_toolchain_version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#]=======================================================================]
macro(_cudatoolkit_toolchain_version toolkit_version nvcc_executable toolkit_path)
    set(${toolkit_version} "${toolkit_version}-NOTFOUND")
    if (NOT ${toolkit_version})
        _cudatoolkit_toolchain_version_txt(${toolkit_version} "${toolkit_path}")
    endif()
    if (NOT ${toolkit_version})
        _cudatoolkit_toolchain_version_json(${toolkit_version} "${toolkit_path}")
    endif()
    if (NOT ${toolkit_version})
        _cudatoolkit_toolchain_version_nvcc(${toolkit_version} "${nvcc_executable}")
    endif()
endmacro()

#[=======================================================================[.rst:
#]=======================================================================]
function(_cudatoolkit_toolchain_split_version toolkit_version_major toolkit_version_minor toolkit_version_patch toolkit_version)
    if("${toolkit_version}" MATCHES [=[([0-9]+)(\.[0-9]+)?(\.[0-9]+)?]=])
      set(version_major "${CMAKE_MATCH_1}")
      set(version_minor "0")
      if(CMAKE_MATCH_COUNT GREATER 1)
        string(SUBSTRING "${CMAKE_MATCH_2}" 1 -1 version_minor)
      endif()
      set(version_patch "0")
      if(CMAKE_MATCH_COUNT GREATER 2)
        string(SUBSTRING "${CMAKE_MATCH_3}" 1 -1 version_patch)
      endif()
      set(${toolkit_version_major} "${version_major}" PARENT_SCOPE)
      set(${toolkit_version_minor} "${version_minor}" PARENT_SCOPE)
      set(${toolkit_version_patch} "${version_patch}" PARENT_SCOPE)
    else()
      unset(${toolkit_version_major} "${toolkit_version_major}-NOTFOUND" PARENT_SCOPE)
      unset(${toolkit_version_minor} "${toolkit_version_minor}-NOTFOUND" PARENT_SCOPE)
      unset(${toolkit_version_patch} "${toolkit_version_patch}-NOTFOUND" PARENT_SCOPE)
    endif()
endfunction()

#[=======================================================================[.rst:
Parse visual studio integration configuration for cuda version
#]=======================================================================]
function(_cudatoolkit_toolchain_version_msbuild toolkit_version custom_target_path)
  if(NOT EXISTS "${custom_target_path}")
    unset(${toolkit_version} PARENT_SCOPE)
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
        set(${toolkit_version}
            "${CMAKE_MATCH_1}"
            PARENT_SCOPE)
      elseif(CMAKE_MATCH_COUNT EQUAL 2)
        set(${toolkit_version}
            "${CMAKE_MATCH_1}${CMAKE_MATCH_2}"
            PARENT_SCOPE)
      elseif(CMAKE_MATCH_COUNT EQUAL 3)
        set(${toolkit_version}
            "${CMAKE_MATCH_1}${CMAKE_MATCH_2}${CMAKE_MATCH_3}"
            PARENT_SCOPE)
      endif()
    endif()
  endif()
endfunction()

#[=======================================================================[.rst:
_cudatoolkit_toolchain_architectures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Parse cuda architectures from nvcc
#]=======================================================================]
function(_cudatoolkit_toolchain_architectures cuda_architectures nvcc_executable)
    if (DEFINED CMAKE_CUDA_ARCHITECTURES AND NOT "${CMAKE_CUDA_ARCHITECTURES}" STREQUAL "")
        set(${cuda_architectures} "${CMAKE_CUDA_ARCHITECTURES}" PARENT_SCOPE)
        return()
    endif()
    if (DEFINED ENV{CUDAARCHS} AND NOT "$ENV{CUDAARCHS}" STREQUAL "")
        set(${cuda_architectures} "$ENV{CUDAARCHS}" PARENT_SCOPE)
        return()
    endif()

    if(NOT EXISTS "${nvcc_executable}")
        set(${cuda_architectures} "${cuda_architectures}-NOTFOUND" PARENT_SCOPE)
        return()
    endif()
    execute_process(COMMAND ${nvcc_executable} "--list-gpu-arch"
        OUTPUT_VARIABLE nvcc_arch_output)
    string(REGEX REPLACE "\n" ";" nvcc_arch_lines "${nvcc_arch_output}")
    unset(nvcc_arch)
    foreach (line IN LISTS nvcc_arch_lines)
        if("${line}" MATCHES [=[compute_([0-9]+)]=])
            list(APPEND nvcc_arch "${CMAKE_MATCH_1}")
        endif()
    endforeach()
    list(REMOVE_DUPLICATES nvcc_arch)
    if (NOT "${nvcc_arch}" STREQUAL "")
        set(${cuda_architectures} "${nvcc_arch}" PARENT_SCOPE)
    else()
        set(${cuda_architectures} "${cuda_architectures}-NOTFOUND" PARENT_SCOPE)
    endif()
endfunction()

#[=======================================================================[.rst:
Result variables
^^^^^^^^^^^^^^^^

``CMAKE_VS_PLATFORM_TOOLSET_CUDA``
    Set to version of "CUDA *.props" for MSVC

For parity with FindCUDAToolkit.cmake will set variables

``CUDAToolkit_FOUND``
    A boolean specifying whether or not the CUDA Toolkit was found.

``CUDAToolkit_VERSION``
    The exact version of the CUDA Toolkit found (as reported by
    ``nvcc --version`` or ``version.txt``).

``CUDAToolkit_VERSION_MAJOR``
    The major version of the CUDA Toolkit.

``CUDAToolkit_VERSION_MAJOR``
    The minor version of the CUDA Toolkit.

``CUDAToolkit_VERSION_PATCH``
    The patch version of the CUDA Toolkit.

``CUDAToolkit_BIN_DIR``
    The path to the CUDA Toolkit library directory that contains the CUDA
    executable ``nvcc``.

``CUDAToolkit_INCLUDE_DIRS``
    The path to the CUDA Toolkit ``include`` folder containing the header files
    required to compile a project linking against CUDA.

``CUDAToolkit_LIBRARY_DIR``
    The path to the CUDA Toolkit library directory that contains the CUDA
    Runtime library ``cudart``.

``CUDAToolkit_LIBRARY_ROOT``
    .. versionadded:: 3.18

    The path to the CUDA Toolkit directory containing the nvvm directory and
    version.txt.

``CUDAToolkit_TARGET_DIR``
    The path to the CUDA Toolkit directory including the target architecture
    when cross-compiling. When not cross-compiling this will be equivalent to
    the parent directory of ``CUDAToolkit_BIN_DIR``.

``CUDAToolkit_NVCC_EXECUTABLE``
    The path to the NVIDIA CUDA compiler ``nvcc``.  Note that this path may
    **not** be the same as
    :variable:`CMAKE_CUDA_COMPILER <CMAKE_<LANG>_COMPILER>`.  ``nvcc`` must be
    found to determine the CUDA Toolkit version as well as determining other
    features of the Toolkit.  This variable is set for the convenience of
    modules that depend on this one.
#]=======================================================================]
function(_cudatoolkit_toolchain package_path)
  set(cuda_version "")
  set(nvcc_dir "")
  set(int_dir "")
  if(EXISTS "${package_path}/nvcc")
    set(nvcc_dir "/nvcc")
  endif()
  if(EXISTS "${package_path}/CUDAVisualStudioIntegration")
    set(int_dir "/CUDAVisualStudioIntegration")
  endif()

  # find CUDAToolkit_LIBRARY_ROOT
  set(cudatoolkit_library_root "${package_path}${nvcc_dir}")
  if (NOT (EXISTS "${cudatoolkit_library_root}/nvvm" AND (EXISTS "${cudatoolkit_library_root}/version.txt" OR EXISTS "${cudatoolkit_library_root}/version.json")))
      message(FATAL_ERROR "CUDA Tolkit library root does not exists: ${cudatoolkit_library_root}")
      return()
  endif()

  # find CUDAToolkit_INCLUDE_DIRS
  set(cudatoolkit_include_dirs "${cudatoolkit_library_root}/include")
  if (NOT EXISTS "${cudatoolkit_include_dirs}")
    message(FATAL_ERROR "CUDA Tolkit include directory does not exists: ${cudatoolkit_bin_dir}")
    return()
  endif()

  set(cudatoolkit_library_dir "${cudatoolkit_library_root}/lib/x64")
  if(NOT EXISTS "${cudatoolkit_library_dir}")
    message(FATAL_ERROR "CUDA Tolkit library directory does not exists: ${cudatoolkit_library_dir}")
    return()
  endif()
  # find CUDAToolkit_BIN_DIR & CUDAToolkit_TARGET_DIR
  set(cudatoolkit_bin_dir "${cudatoolkit_library_root}/bin")
  set(cudatoolkit_target_dir "${cudatoolkit_library_root}")
  if (NOT EXISTS "${cudatoolkit_bin_dir}")
    message(FATAL_ERROR "CUDA Tolkit binary directory does not exists: ${cudatoolkit_bin_dir}")
    return()
  endif()

  # find CUDAToolkit_NVCC_EXECUTABLE
  find_program(
    cudatoolkit_nvcc_executable nvcc
    PATHS "${cudatoolkit_bin_dir}" NO_CACHE
    NO_DEFAULT_PATH NO_PACKAGE_ROOT_PATH NO_CMAKE_PATH
    NO_CMAKE_ENVIRONMENT_PATH NO_SYSTEM_ENVIRONMENT_PATH NO_CMAKE_SYSTEM_PATH)
  if (NOT cudatoolkit_nvcc_executable)
    message(FATAL_ERROR "CUDA nvcc comipler cannot be found in: ${cudatoolkit_bin_dir}")
    return()
  endif()

  # find CUDAToolkit_VERSION & CUDAToolkit_VERSION_MAJOR & CUDAToolkit_VERSION_MINOR & CUDAToolkit_VERSION_PATCH
  _cudatoolkit_toolchain_version(cudatoolkit_version "${cudatoolkit_nvcc_executable}" "${cudatoolkit_library_root}")
  if (NOT cudatoolkit_version)
    message(FATAL_ERROR "Cannot detect CUDAToolkit version")
    return()
  endif()
  _cudatoolkit_toolchain_split_version(cudatoolkit_version_major cudatoolkit_version_minor cudatoolkit_version_patch "${cudatoolkit_version}")

  if (MSVC)
    _cudatoolkit_toolchain_version_msbuild(vs_platform_toolset_cuda "${package_path}${int_dir}/extras/visual_studio_integration/MSBuildExtensions")
    if (NOT vs_platform_toolset_cuda)
        set(vs_platform_toolset_cuda "${cudatoolkit_version}")
    endif()
    set(vs_platform_toolset_cuda_custom_dir "${package_path}")
    # for some reason this need to be set (value exists in format XX.Y during startup under MSVS)
    set(CMAKE_VS_PLATFORM_TOOLSET_CUDA "${vs_platform_toolset_cuda}" PARENT_SCOPE)
    set(CMAKE_VS_PLATFORM_TOOLSET_CUDA "${vs_platform_toolset_cuda}" CACHE INTERNAL "TOOLSET_CUDA" FORCE)
    set(CMAKE_VS_PLATFORM_TOOLSET_CUDA_CUSTOM_DIR "${vs_platform_toolset_cuda_custom_dir}/" CACHE INTERNAL "TOOLSET_CUDA_CUSTOM_DIR" FORCE)
  endif()


  #set(CUDAToolkit_FOUND TRUE)
  set(CUDAToolkit_LIBRARY_ROOT "${cudatoolkit_library_root}" PARENT_SCOPE)
  set(CUDAToolkit_LIBRARY_DIR "${cudatoolkit_library_dir}" PARENT_SCOPE)
  set(CUDAToolkit_BIN_DIR "${cudatoolkit_bin_dir}" PARENT_SCOPE)
  set(CUDAToolkit_NVCC_EXECUTABLE "${cudatoolkit_nvcc_executable}" PARENT_SCOPE)
  set(CMAKE_CUDA_COMPILER "${cudatoolkit_nvcc_executable}" CACHE FILEPATH "CUDA COMPILER" FORCE)

  set(CUDAToolkit_VERSION "${cudatoolkit_version}" PARENT_SCOPE)
  set(CUDAToolkit_VERSION_MAJOR "${cudatoolkit_version_major}" PARENT_SCOPE)
  set(CUDAToolkit_VERSION_MINOR "${cudatoolkit_version_minor}" PARENT_SCOPE)
  set(CUDAToolkit_VERSION_MINOR "${cudatoolkit_version_patch}" PARENT_SCOPE)
  set(CUDAToolkit_INCLUDE_DIRS "${cudatoolkit_include_dirs}" PARENT_SCOPE)
  set(CUDAToolkit_TARGET_DIR "${cudatoolkit_target_dir}" PARENT_SCOPE)
  #set(CUDAToolkit_ROOT "${package_path}" PARENT_SCOPE)
  #set(CUDAToolkit_ROOT "${package_path}" CACHE PATH "CUDA Toolkit root" FORCE)

  _cudatoolkit_toolchain_architectures(toolkit_architectures "${cudatoolkit_nvcc_executable}")
  set(CMAKE_CUDA_ARCHITECTURES "${toolkit_architectures}" CACHE STRING "CUDA Architectures" FORCE)
  set(CMAKE_CUDA_ARCHITECTURES "${toolkit_architectures}" PARENT_SCOPE)

endfunction()

_cudatoolkit_toolchain("${CMAKE_CURRENT_LIST_DIR}")
