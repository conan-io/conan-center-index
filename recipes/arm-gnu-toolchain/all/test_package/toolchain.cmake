# Append current directory to CMAKE_MODULE_PATH for making device specific
# cmake modules visible
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})

# Target definition
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR ARM)
set(TOOLCHAIN arm-none-eabi)

# Perform compiler test with static library
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

# ------------------------------------------------------------------------------
# Set compilers
# ------------------------------------------------------------------------------
set(CMAKE_C_COMPILER ${TOOLCHAIN}-gcc${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_CXX_COMPILER ${TOOLCHAIN}-g++${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_ASM_COMPILER ${TOOLCHAIN}-gcc${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_SIZE_UTIL ${TOOLCHAIN}-size${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_OBJDUMP ${TOOLCHAIN}-objdump${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_OBJCOPY ${TOOLCHAIN}-objcopy${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_FIND_ROOT_PATH ${CMAKE_PREFIX_PATH} ${CMAKE_BINARY_DIR})

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
