#include <cgif.h>

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define WIDTH 1024
#define HEIGHT 1024

static void initGIFConfig(CGIF_Config *pConfig, char *path, uint16_t width,
                          uint16_t height, uint8_t *pPalette,
                          uint16_t numColors)
{
    memset(pConfig, 0, sizeof(CGIF_Config));
    pConfig->width = width;
    pConfig->height = height;
    pConfig->pGlobalPalette = pPalette;
    pConfig->numGlobalPaletteEntries = numColors;
    pConfig->path = path;
}

static void initFrameConfig(CGIF_FrameConfig *pConfig, uint8_t *pImageData)
{
    memset(pConfig, 0, sizeof(CGIF_FrameConfig));
    pConfig->pImageData = pImageData;
}

int main()
{
    CGIF *pGIF;
    CGIF_Config gConfig;
    CGIF_FrameConfig fConfig;
    uint8_t *pImageData;
    uint8_t aPalette[] = {0xFF, 0x00, 0x00,
                          0x00, 0xFF, 0x00,
                          0x00, 0x00, 0xFF};
    uint16_t numColors = 3;

    initGIFConfig(&gConfig, "example_cgif.gif", WIDTH, HEIGHT, aPalette, numColors);
    pGIF = cgif_newgif(&gConfig);

    pImageData = malloc(WIDTH * HEIGHT);
    for (int i = 0; i < (WIDTH * HEIGHT); ++i) {
        pImageData[i] = (unsigned char)((i % WIDTH) / 4 % numColors);
    }

    initFrameConfig(&fConfig, pImageData);
    cgif_addframe(pGIF, &fConfig);
    free(pImageData);

    cgif_close(pGIF);
    return 0;
}
