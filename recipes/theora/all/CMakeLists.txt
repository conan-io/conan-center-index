cmake_minimum_required(VERSION 3.15)
project(theora C)

find_package(Ogg REQUIRED)

set (HEADERS
  "include/theora/codec.h"
  "include/theora/theora.h"
  "include/theora/theoradec.h"
  "include/theora/theoraenc.h"
)

set(LIBTHEORA_COMMON
   "lib/apiwrapper.c"
   "lib/bitpack.c"   # was not in enc in SConstruct
   "lib/dequant.c"
   "lib/fragment.c"
   "lib/idct.c"
   "lib/info.c"   # was not in enc in SConstruct
   "lib/internal.c"
   "lib/state.c"
   "lib/quant.c"
   )

set(LIBTHEORA_ENC
   "lib/analyze.c"
   "lib/encapiwrapper.c"
   "lib/encfrag.c"
   "lib/encinfo.c"
   "lib/encode.c"
   "lib/enquant.c"
   "lib/fdct.c"
   "lib/huffenc.c"
   "lib/mathops.c"
   "lib/mcenc.c"
   "lib/rate.c"
   "lib/tokenize.c"
   )


set(LIBTHEORA_DEC
   "lib/decapiwrapper.c"
   "lib/decinfo.c"
   "lib/decode.c"
   "lib/huffdec.c"
   )


option(USE_X86_32 "Use x86-32 optimization" OFF)
option(USE_X86_64 "Use x86-64 optimization" OFF)
if (USE_X86_32)
   message("Enabling x86-32 assembly optimizations")
   add_definitions(-DOC_X86_ASM)

   list (APPEND LIBTHEORA_COMMON
      "lib/x86/mmxidct.c"
      "lib/x86/mmxfrag.c"
      "lib/x86/mmxstate.c"
      "lib/x86/x86state.c"
      )

   list (APPEND LIBTHEORA_ENC
      "lib/x86/mmxencfrag.c"
      "lib/x86/mmxfdct.c"
      "lib/x86/x86enc.c"
      "lib/x86/mmxfrag.c"
      "lib/x86/mmxidct.c"
      "lib/x86/mmxstate.c"
      "lib/x86/x86state.c"
      )
elseif (USE_X86_64)
   message("Enabling x86-64 assembly optimizations")
   add_definitions(-DOC_X86_ASM)
   add_definitions(-DOC_X86_64_ASM)

   list (APPEND LIBTHEORA_COMMON
      "lib/x86/mmxidct.c"
      "lib/x86/mmxfrag.c"
      "lib/x86/mmxstate.c"
      "lib/x86/x86state.c"
      )

   list (APPEND LIBTHEORA_ENC
      "lib/x86/mmxencfrag.c"
      "lib/x86/mmxfdct.c"
      "lib/x86/x86enc.c"
      "lib/x86/sse2fdct.c"
      )
else()
   message("Not enabling any assembly optimizations (x86 and x86_64 asm optimizations are available)")
endif()

add_definitions(-D_CRT_SECURE_NO_DEPRECATE)
add_definitions(-D_CRT_NONSTDC_NO_DEPRECATE)


if (BUILD_SHARED_LIBS)
  add_definitions(-DLIBTHEORA_EXPORTS)
endif()


add_library(theora ${LIBTHEORA_COMMON} ${LIBTHEORA_ENC} ${LIBTHEORA_DEC} "lib/theora.def")
target_link_libraries(theora PUBLIC Ogg::ogg)
target_include_directories(theora PUBLIC include)

add_library(theoraenc ${LIBTHEORA_COMMON} ${LIBTHEORA_ENC} "win32/xmingw32/libtheoraenc-all.def")
target_link_libraries(theoraenc PUBLIC Ogg::ogg)
target_include_directories(theoraenc PUBLIC include)

add_library(theoradec ${LIBTHEORA_COMMON} ${LIBTHEORA_DEC} "win32/xmingw32/libtheoradec-all.def")
target_link_libraries(theoradec PUBLIC Ogg::ogg)
target_include_directories(theoradec PUBLIC include)

# note: the original recipe generated libtheora.dll on Windows
# So we do this to be consistent with the original outputs.
set_target_properties(theora PROPERTIES PREFIX "lib")
set_target_properties(theoraenc PROPERTIES PREFIX "lib")
set_target_properties(theoradec PROPERTIES PREFIX "lib")

install(FILES ${HEADERS} DESTINATION include/theora)
install(TARGETS theora theoraenc theoradec)
