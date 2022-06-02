# SPDX-License-Identifier: MIT Copyright (c) 2022 Jai Bellare See
# <https://opensource.org/licenses/MIT/> or LICENSE.md Project homepage:
# <https://github.com/strangeQuark1041/samarium>

cmake_minimum_required(VERSION 3.16)

function(iwyu IWYU_TARGET)
    if(USE_IWYU)
        find_program(iwyu_path NAMES include-what-you-use iwyu REQUIRED)
        set_property(TARGET ${IWYU_TARGET} PROPERTY CXX_INCLUDE_WHAT_YOU_USE ${iwyu_path})
    endif()
endfunction()
