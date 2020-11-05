// Copyright Twitch Interactive, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT

#include <libsoundtrackutil/SoundtrackIPC.h>

using namespace Twitch::Audio;

int main()
{
    SoundtrackIPC soundtrackIPC({[]() {}, []() {}, [](TwitchAudioPacket audioPacket) {}});
}
