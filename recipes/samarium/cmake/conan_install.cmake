# SPDX-License-Identifier: MIT Copyright (c) 2022 Jai Bellare See
# <https://opensource.org/licenses/MIT/> or LICENSE.md Project homepage:
# <https://github.com/strangeQuark1041/samarium>

if(NOT EXISTS ${CMAKE_BINARY_DIR}/conan.lock)
    include(conan)

    conan_cmake_autodetect(settings)

    message(STATUS "Installing Conan dependencies... (this may take a few minutes)")
    conan_cmake_install(
        PATH_OR_REFERENCE
        ${CMAKE_SOURCE_DIR}
        BUILD
        missing
        REMOTE
        conancenter
        SETTINGS
        ${settings}
        OUTPUT_QUIET
    )
else()
    message(STATUS "Conan dependencies already installed")
endif()
