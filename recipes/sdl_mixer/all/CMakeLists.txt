cmake_minimum_required(VERSION 3.15)
project(sdl2_mixer LANGUAGES C)

include(CheckTypeSize)

macro(add_music_option type)
  option(${type} "${type} music support" OFF)
  message(STATUS "${type} ${${type}}")
  if(${${type}})
    add_definitions("-DMUSIC_${type}")
    if(${${type}_DYNAMIC})
      add_definitions("-D${type}_DYNAMIC")
    endif()
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

if(${MID_NATIVE})
    set(NATIVE_MIDI_SOURCES
        ${SDL_MIXER_SRC_DIR}/native_midi/native_midi_common.c
        ${SDL_MIXER_SRC_DIR}/native_midi/native_midi_common.h
        ${SDL_MIXER_SRC_DIR}/native_midi/native_midi_haiku.cpp
        ${SDL_MIXER_SRC_DIR}/native_midi/native_midi_mac.c
        ${SDL_MIXER_SRC_DIR}/native_midi/native_midi_macosx.c
        ${SDL_MIXER_SRC_DIR}/native_midi/native_midi_win32.c
    )

    set(NATIVE_MIDI_HEADERS
        ${SDL_MIXER_SRC_DIR}/native_midi/native_midi.h
    )
endif()

set(SOURCES
    ${SDL_MIXER_SRC_DIR}/effect_position.c
    ${SDL_MIXER_SRC_DIR}/effect_stereoreverse.c
    ${SDL_MIXER_SRC_DIR}/effects_internal.c
    ${SDL_MIXER_SRC_DIR}/load_aiff.c
    ${SDL_MIXER_SRC_DIR}/load_voc.c
    ${SDL_MIXER_SRC_DIR}/mixer.c
    ${SDL_MIXER_SRC_DIR}/music.c
    ${SDL_MIXER_SRC_DIR}/music_cmd.c
    ${SDL_MIXER_SRC_DIR}/music_flac.c
    ${SDL_MIXER_SRC_DIR}/music_fluidsynth.c
    ${SDL_MIXER_SRC_DIR}/music_mad.c
    ${SDL_MIXER_SRC_DIR}/music_mikmod.c
    ${SDL_MIXER_SRC_DIR}/music_modplug.c
    ${SDL_MIXER_SRC_DIR}/music_mpg123.c
    ${SDL_MIXER_SRC_DIR}/music_nativemidi.c
    ${SDL_MIXER_SRC_DIR}/music_ogg.c
    ${SDL_MIXER_SRC_DIR}/music_opus.c
    ${SDL_MIXER_SRC_DIR}/music_timidity.c
    ${SDL_MIXER_SRC_DIR}/music_wav.c
    ${NATIVE_MIDI_SOURCES}
)

set(HEADERS
    ${SDL_MIXER_SRC_DIR}/effects_internal.h
    ${SDL_MIXER_SRC_DIR}/load_aiff.h
    ${SDL_MIXER_SRC_DIR}/load_voc.h
    ${SDL_MIXER_SRC_DIR}/mixer.h
    ${SDL_MIXER_SRC_DIR}/music.h
    ${SDL_MIXER_SRC_DIR}/music_cmd.h
    ${SDL_MIXER_SRC_DIR}/music_flac.h
    ${SDL_MIXER_SRC_DIR}/music_fluidsynth.h
    ${SDL_MIXER_SRC_DIR}/music_mad.h
    ${SDL_MIXER_SRC_DIR}/music_mikmod.h
    ${SDL_MIXER_SRC_DIR}/music_modplug.h
    ${SDL_MIXER_SRC_DIR}/music_mpg123.h
    ${SDL_MIXER_SRC_DIR}/music_nativemidi.h
    ${SDL_MIXER_SRC_DIR}/music_ogg.h
    ${SDL_MIXER_SRC_DIR}/music_opus.h
    ${SDL_MIXER_SRC_DIR}/music_timidity.h
    ${SDL_MIXER_SRC_DIR}/music_wav.h
    ${NATIVE_MIDI_HEADERS}
)

add_library(${PROJECT_NAME} ${SOURCES} ${HEADERS})

target_include_directories(${PROJECT_NAME} PRIVATE ${SDL_MIXER_SRC_DIR})

if(${MID_NATIVE})
    target_include_directories(${PROJECT_NAME} PRIVATE ${SDL_MIXER_SRC_DIR}/native_midi)
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

set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER ${SDL_MIXER_SRC_DIR}/SDL_mixer.h)

if(${BUILD_SHARED_LIBS})
  target_compile_definitions(${PROJECT_NAME} PRIVATE DLL_EXPORT)
endif()

set_target_properties(${PROJECT_NAME} PROPERTIES OUTPUT_NAME "SDL2_mixer")

check_type_size("ssize_t" SSIZE_T)
if(SSIZE_T STREQUAL "")
  target_compile_definitions(${PROJECT_NAME} PRIVATE ssize_t=signed) # non-standard type
endif()

install(TARGETS ${PROJECT_NAME}
  ARCHIVE DESTINATION "lib"
  LIBRARY DESTINATION "lib"
  RUNTIME DESTINATION "bin"
  PUBLIC_HEADER DESTINATION "include/SDL2"
)
