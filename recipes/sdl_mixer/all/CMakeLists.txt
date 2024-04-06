cmake_minimum_required(VERSION 3.15)
project(sdl2_mixer)

include(CheckTypeSize)

macro(add_music_option type)
  option(${type} "${type} music support" OFF)
  message(STATUS "${type} ${${type}}")
  if(${type})
    add_definitions("-DMUSIC_${type}")
  endif()
endmacro()

add_music_option(CMD)
add_music_option(WAV)
add_music_option(FLAC)
add_music_option(OGG)
add_music_option(OPUS)
add_music_option(MP3_MPG123)
add_music_option(MP3_MAD)
add_music_option(MOD_MIKMOD)
add_music_option(MOD_MODPLUG)
add_music_option(MID_NATIVE)
add_music_option(MID_FLUIDSYNTH)
add_music_option(MID_TINYMIDI)

if(MIDI_NATIVE)
  set(NATIVE_MIDI_SOURCES
    src/native_midi/native_midi_common.c
    src/native_midi/native_midi_common.h
    src/native_midi/native_midi_haiku.cpp
    src/native_midi/native_midi_mac.c
    src/native_midi/native_midi_macosx.c
    src/native_midi/native_midi_win32.c
  )

  set(NATIVE_MIDI_HEADERS
    src/native_midi/native_midi.h
  )
endif()

set(SOURCES
  src/effect_position.c
  src/effect_stereoreverse.c
  src/effects_internal.c
  src/load_aiff.c
  src/load_voc.c
  src/mixer.c
  src/music.c
  src/music_cmd.c
  src/music_flac.c
  src/music_fluidsynth.c
  src/music_mad.c
  src/music_mikmod.c
  src/music_modplug.c
  src/music_mpg123.c
  src/music_nativemidi.c
  src/music_ogg.c
  src/music_opus.c
  src/music_timidity.c
  src/music_wav.c
  ${NATIVE_MIDI_SOURCES}
)

set(HEADERS
  src/effects_internal.h
  src/load_aiff.h
  src/load_voc.h
  src/mixer.h
  src/music.h
  src/music_cmd.h
  src/music_flac.h
  src/music_fluidsynth.h
  src/music_mad.h
  src/music_mikmod.h
  src/music_modplug.h
  src/music_mpg123.h
  src/music_nativemidi.h
  src/music_ogg.h
  src/music_opus.h
  src/music_timidity.h
  src/music_wav.h
  ${NATIVE_MIDI_HEADERS}
)

add_library(${PROJECT_NAME} ${SOURCES} ${HEADERS})

target_include_directories(${PROJECT_NAME} PRIVATE "src")

if(MIDI_NATIVE)
  target_include_directories(${PROJECT_NAME} PRIVATE "src/native_midi")
  if(APPLE)
    # https://github.com/libsdl-org/SDL_mixer/blob/release-2.0.4/configure.in#L380
    target_link_libraries(${PROJECT_NAME} PRIVATE "-framework AudioToolbox" "-framework AudioUnit" "-framework CoreServices")
  elseif(WIN32)
    # https://github.com/libsdl-org/SDL_mixer/blob/release-2.0.4/configure.in#L376
    target_link_libraries(${PROJECT_NAME} PRIVATE winmm)
  endif()
endif()

find_package(SDL2 CONFIG REQUIRED)

if(TARGET SDL2::SDL2-static)
    target_link_libraries(${PROJECT_NAME} PRIVATE SDL2::SDL2-static)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE SDL2::SDL2)
endif()
if(FLAC)
  find_package(flac CONFIG REQUIRED)
  target_link_libraries(${PROJECT_NAME} PRIVATE FLAC::FLAC++)
endif()
if(OGG)
  find_package(Ogg CONFIG REQUIRED)
  find_package(Vorbis CONFIG REQUIRED)
  target_link_libraries(${PROJECT_NAME} PRIVATE Ogg::ogg Vorbis::vorbisfile)
endif()
if(OPUS)
  find_package(Opus CONFIG REQUIRED)
  find_package(opusfile CONFIG REQUIRED)
  find_package(OpenSSL CONFIG REQUIRED)
  target_link_libraries(${PROJECT_NAME} PRIVATE Opus::opus opusfile::opusfile OpenSSL::SSL)
endif()
if(MP3_MPG123)
  find_package(mpg123 CONFIG REQUIRED)
  target_link_libraries(${PROJECT_NAME} PRIVATE MPG123::libmpg123)
endif()
if(MP3_MAD)
  find_package(libmad CONFIG REQUIRED)
  target_link_libraries(${PROJECT_NAME} PRIVATE libmad::libmad)
endif()
if(MOD_MIKMOD)
  find_package(libmikmod CONFIG REQUIRED)
  target_link_libraries(${PROJECT_NAME} PRIVATE libmikmod::libmikmod)
endif()
if(MOD_MODPLUG)
  find_package(libmodplug CONFIG REQUIRED)
  target_link_libraries(${PROJECT_NAME} PRIVATE libmodplug::libmodplug)
endif()
if(MID_FLUIDSYNTH)
  find_package(fluidsynth CONFIG REQUIRED)
  target_link_libraries(${PROJECT_NAME} PRIVATE fluidsynth::fluidsynth)
endif()
if(MID_TINYMIDI)
  find_package(tinymidi CONFIG REQUIRED)
  target_link_libraries(${PROJECT_NAME} PRIVATE tinymidi::tinymidi)
endif()

set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER src/SDL_mixer.h)

if(BUILD_SHARED_LIBS)
  target_compile_definitions(${PROJECT_NAME} PRIVATE DLL_EXPORT)
endif()

set_target_properties(${PROJECT_NAME} PROPERTIES OUTPUT_NAME "SDL2_mixer")

check_type_size("ssize_t" SSIZE_T)
if(SSIZE_T STREQUAL "")
  target_compile_definitions(${PROJECT_NAME} PRIVATE ssize_t=signed) # non-standard type
endif()

install(TARGETS ${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
  PUBLIC_HEADER DESTINATION include/SDL2
)
