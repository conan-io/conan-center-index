# Reproduce the official CMake config: https://github.com/pulseaudio/pulseaudio/blob/v16.1/PulseAudioConfig.cmake.in

set(PULSEAUDIO_FOUND TRUE)

set(PULSEAUDIO_VERSION_MAJOR ${PulseAudio_VERSION_MAJOR})
set(PULSEAUDIO_VERSION_MINOR ${PulseAudio_VERSION_MINOR})
set(PULSEAUDIO_VERSION ${PulseAudio_VERSION_MAJOR}.${PulseAudio_VERSION_MINOR})
set(PULSEAUDIO_VERSION_STRING "${PulseAudio_VERSION_MAJOR}.${PulseAudio_VERSION_MINOR}")

set(PULSEAUDIO_INCLUDE_DIR ${PulseAudio_INCLUDE_DIR})
set(PULSEAUDIO_LIBRARY ${PulseAudio_LIBRARIES})

# Make sure PULSEAUDIO_LIBRARY uses an absolute path for non-targets, so it can be used without target_link_directories()
list (GET PULSEAUDIO_INCLUDE_DIR 0 _first_include_dir)
get_filename_component(PULSEAUDIO_LIB_DIRS  "${_first_include_dir}/../lib" ABSOLUTE)
foreach(_LIB ${PulseAudio_LIBRARIES})
    if(TARGET ${_LIB})
        list(APPEND PULSEAUDIO_LIBRARY ${_LIB})
    else()
        list(APPEND PULSEAUDIO_LIBRARY ${PULSEAUDIO_LIB_DIRS}/${_LIB})
    endif()
endforeach()

if(pulse-mainloop-glib IN_LIST PulseAudio_LIBRARIES)
    set(PULSEAUDIO_MAINLOOP_LIBRARY pulse-mainloop-glib)
elif(libpulse-mainloop-glib IN_LIST PulseAudio_LIBRARIES)
    set(PULSEAUDIO_MAINLOOP_LIBRARY libpulse-mainloop-glib)
endif()
