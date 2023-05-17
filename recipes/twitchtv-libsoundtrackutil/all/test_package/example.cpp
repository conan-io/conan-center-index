#include <libsoundtrackutil/SoundtrackIPC.h>

using namespace Twitch::Audio;

int main()
{
    SoundtrackIPC soundtrackIPC({[]() {}, []() {}, [](TwitchAudioPacket audioPacket) {}});
}
