#include <SDL.h>
#include <stdexcept>
#include <string>
#include <sstream>
#include <iostream>
#include <cstdlib>

static void throw_exception(const char * message, const char * name)
{
    std::stringstream s;
    s << message << " - " << name;
    throw std::runtime_error(s.str().c_str());
}

static void check_audio_driver(const char * name)
{
    std::cout << "checking for audio driver " << name << " ... ";
    bool found = false;
    int count = SDL_GetNumAudioDrivers();
    for (int i = 0; i < count; ++i) {
        if (0 == strcmp(name, SDL_GetAudioDriver(i))) {
            found = true;
            break;
        }
    }
    if (!found)
        throw_exception("audio driver wasn't found", name);
    std::cout << "OK!" << std::endl;
}

static void check_video_driver(const char * name)
{
    std::cout << "checking for video driver " << name << " ... ";
    bool found = false;
    int count = SDL_GetNumVideoDrivers();
    for (int i = 0; i < count; ++i) {
        if (0 == strcmp(name, SDL_GetVideoDriver(i))) {
            found = true;
            break;
        }
    }
    if (!found)
        throw_exception("video driver wasn't found", name);
    std::cout << "OK!" << std::endl;
}


int main(int argc, char *argv[]) try
{
    SDL_version v;
    SDL_GetVersion(&v);
    std::cout << "SDL version " << int(v.major) << "." << int(v.minor) << "." << int(v.patch) << std::endl;
#ifdef WITH_X11
    check_video_driver("x11");
#endif
#ifdef WITH_ALSA
    check_audio_driver("alsa");
#endif
#ifdef WITH_PULSE
    check_audio_driver("pulseaudio");
#endif
#ifdef WITH_ESD
    check_audio_driver("esd");
#endif
#ifdef WITH_ARTS
    check_audio_driver("arts");
#endif
#ifdef WITH_DIRECTFB
    check_video_driver("directfb");
#endif
#ifdef WITH_DIRECTX
    check_audio_driver("directsound");
#endif
    return EXIT_SUCCESS;
}
catch (std::runtime_error & e)
{
    std::cout << "FAIL!" << std::endl;
    std::cerr << e.what() << std::endl;
    return EXIT_FAILURE;
}
