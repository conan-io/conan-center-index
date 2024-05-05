#
# Copyright(c) 2020 to 2022 ZettaScale Technology and others
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v. 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0, or the Eclipse Distribution License
# v. 1.0 which is available at
# http://www.eclipse.org/org/documents/edl-v10.php.
#
# SPDX-License-Identifier: EPL-2.0 OR BSD-3-Clause
#

# NOTE: This function was leveraged from the upstream cyclonedds-cxx project
# and modified to find the direct path to the cycloneddsidlcxx library as
# opposed to leveraging the native CycloneDDS-CXX::idlcxx cmake target.
# Because Conan redeclares its own targets using INTERFACE libs, the upstream
# version of this function was incompatible. If the upstream implementation of
# this functionality changes, a modification to this file may be required.
# See: https://github.com/eclipse-cyclonedds/cyclonedds-cxx/blob/master/src/idlcxx/Generate.cmake

find_package(CycloneDDS REQUIRED)

# find idlcxx shared library
set(CMAKE_FIND_LIBRARY_SUFFIXES .dll ${CMAKE_FIND_LIBRARY_SUFFIXES})
if(CMAKE_CROSSCOMPILING)
  find_library(_idlcxx_shared_lib cycloneddsidlcxx NO_CMAKE_FIND_ROOT_PATH REQUIRED)
else()
  find_library(_idlcxx_shared_lib
    NAMES cycloneddsidlcxx
    PATHS ${CMAKE_CURRENT_LIST_DIR}/../../bin/
          ${CMAKE_CURRENT_LIST_DIR}/../../lib/
    NO_DEFAULT_PATH)
endif()

if(_idlcxx_shared_lib)
  set(_idlcxx_depends "")
else()
  message(FATAL_ERROR "Cannot find idlcxx shared library")
endif()

function(IDLCXX_GENERATE)
  set(one_value_keywords TARGET DEFAULT_EXTENSIBILITY BASE_DIR OUTPUT_DIR)
  set(multi_value_keywords FILES FEATURES INCLUDES WARNINGS)
  cmake_parse_arguments(
    IDLCXX "" "${one_value_keywords}" "${multi_value_keywords}" "" ${ARGN})

  idlc_generate_generic(TARGET ${IDLCXX_TARGET}
    BACKEND ${_idlcxx_shared_lib}
    BASE_DIR ${IDLCXX_BASE_DIR}
    FILES ${IDLCXX_FILES}
    FEATURES ${IDLCXX_FEATURES}
    INCLUDES ${IDLCXX_INCLUDES}
    WARNINGS ${IDLCXX_WARNINGS}
    DEFAULT_EXTENSIBILITY ${IDLCXX_DEFAULT_EXTENSIBILITY}
    SUFFIXES .hpp .cpp
    OUTPUT_DIR ${IDLCXX_OUTPUT_DIR}
    DEPENDS ${_idlcxx_depends}
  )
  if(CYCLONEDDS_CXX_ENABLE_LEGACY)
      target_include_directories(${IDLCXX_TARGET}
          INTERFACE ${Boost_INCLUDE_DIR}
      )
  endif()
endfunction()
