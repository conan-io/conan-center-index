# Reproduce the official CMake config: https://github.com/pulseaudio/pulseaudio/blob/v16.1/PulseAudioConfig.cmake.in

set(PULSEAUDIO_FOUND TRUE)

set(PULSEAUDIO_VERSION_MAJOR ${PulseAudio_VERSION_MAJOR})
set(PULSEAUDIO_VERSION_MINOR ${PulseAudio_VERSION_MINOR})
set(PULSEAUDIO_VERSION ${PulseAudio_VERSION_MAJOR}.${PulseAudio_VERSION_MINOR})
set(PULSEAUDIO_VERSION_STRING "${PulseAudio_VERSION_MAJOR}.${PulseAudio_VERSION_MINOR}")

set(PULSEAUDIO_INCLUDE_DIR ${PulseAudio_INCLUDE_DIR})
set(PULSEAUDIO_LIBRARY ${PulseAudio_LIBRARIES})

if(pulse-mainloop-glib IN_LIST PulseAudio_LIBRARIES)
    set(PULSEAUDIO_MAINLOOP_LIBRARY pulse-mainloop-glib)
elif(libpulse-mainloop-glib IN_LIST PulseAudio_LIBRARIES)
    set(PULSEAUDIO_MAINLOOP_LIBRARY libpulse-mainloop-glib)
endif()
