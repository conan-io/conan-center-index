#include <stdio.h>
#include <stdlib.h>
#include <SDL.h>
#include <SDL_mixer.h>

int main(int argc, char *argv[])
{
    int audio_rate = MIX_DEFAULT_FREQUENCY;
    int audio_format = MIX_DEFAULT_FORMAT;
    int audio_channels = 2;
    const SDL_version * version = Mix_Linked_Version();
    printf("%s", "SDL2_mixer version: ");
    printf("%d.", (int)(version->major));
    printf("%d.", (int)(version->minor));
    printf("%d\n", (int)(version->patch));

    if (SDL_Init(SDL_INIT_AUDIO) == 0) {
        int initted = Mix_Init(MIX_INIT_FLAC | MIX_INIT_MOD | MIX_INIT_MP3 | MIX_INIT_OGG | MIX_INIT_MID | MIX_INIT_OPUS);
        printf("%s %s\n", "Supported MIX_INIT_MOD: " , (initted & MIX_INIT_MOD  ? "Yes" : "No"));
        printf("%s %s\n", "Supported MIX_INIT_MP3: " , (initted & MIX_INIT_MP3  ? "Yes" : "No"));
        printf("%s %s\n", "Supported MIX_INIT_OGG: " , (initted & MIX_INIT_OGG  ? "Yes" : "No"));
        printf("%s %s\n", "Supported MIX_INIT_FLAC: ", (initted & MIX_INIT_FLAC ? "Yes" : "No"));
        printf("%s %s\n", "Supported MIX_INIT_MID: " , (initted & MIX_INIT_MID  ? "Yes" : "No"));
        printf("%s %s\n", "Supported MIX_INIT_OPUS: ", (initted & MIX_INIT_OPUS ? "Yes" : "No"));

        if (Mix_OpenAudio(audio_rate, audio_format, audio_channels, 4096) == 0) {
            int num_chunk_decoders = Mix_GetNumChunkDecoders();
            int num_music_decoders = Mix_GetNumMusicDecoders();
            int i = 0;
            printf("%s\n", "chunk decoders:");
            for (i = 0; i < num_chunk_decoders; ++i)
                printf("\t%s\n", Mix_GetChunkDecoder(i));
            printf("%s\n", "music decoders:");
            for (i = 0; i < num_music_decoders; ++i)
                printf("\t%s\n", Mix_GetMusicDecoder(i));
            Mix_CloseAudio();
            Mix_Quit();
        }
    }

    return 0;
}
