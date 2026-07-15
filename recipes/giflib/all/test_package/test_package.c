#include "gif_lib.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LINE_LEN        40
#define IMAGEWIDTH      LINE_LEN*GIF_FONT_WIDTH

static int BackGround = 0;
static void QuitGifError(GifFileType *GifFile);
static void GenRasterTextLine(GifRowType *RasterBuffer, char *TextLine,
        int BufferWidth, int ForeGroundIndex);

/******************************************************************************
 Interpret the command line and generate the given GIF file.
******************************************************************************/
int main(int argc, char **argv)
{
    int i, j, l, ColorMapSize, ErrorCode;
    char Line[LINE_LEN];
    GifRowType RasterBuffer[GIF_FONT_HEIGHT];
    ColorMapObject *ColorMap;
    GifFileType *GifFile;
    GifColorType ScratchMap[256];

    if (argc < 2) {
        fprintf(stderr, "Usage: %s OUTPUTGIF\n", argv[0]);
        exit(1);
    }

    /* Allocate the raster buffer for GIF_FONT_HEIGHT scan lines. */
    for (i = 0; i < GIF_FONT_HEIGHT; i++)
    {
        if ((RasterBuffer[i] = (GifRowType) malloc(sizeof(GifPixelType) * IMAGEWIDTH)) == NULL)
            exit(1);
    }

    /* Open stdout for the output file: */
    if ((GifFile = EGifOpenFileName(argv[1], 0, &ErrorCode)) == NULL) {
        printf("error: %d\n", ErrorCode);
        exit(EXIT_FAILURE);
    }

    /* Read the color map in ColorFile into this color map: */
    for (ColorMapSize = 0; ColorMapSize < 256; ColorMapSize++)
    {
        ScratchMap[ColorMapSize].Red = ColorMapSize;
        ScratchMap[ColorMapSize].Green = ColorMapSize;
        ScratchMap[ColorMapSize].Blue = ColorMapSize;
    }

    if ((ColorMap = GifMakeMapObject(1 << GifBitSize(ColorMapSize), ScratchMap)) == NULL)
        exit(1);

    if (EGifPutScreenDesc(GifFile,
            IMAGEWIDTH, ColorMapSize * GIF_FONT_HEIGHT,
            GifBitSize(ColorMapSize),
            BackGround, ColorMap) == GIF_ERROR)
        QuitGifError(GifFile);

    /* Dump out the image descriptor: */
    if (EGifPutImageDesc(GifFile,
    0, 0, IMAGEWIDTH, ColorMapSize * GIF_FONT_HEIGHT, false, NULL) == GIF_ERROR)
    QuitGifError(GifFile);

    printf("\n%s: Image 1 at (%d, %d) [%dx%d]:     \n",
            "test_package", GifFile->Image.Left, GifFile->Image.Top,
            GifFile->Image.Width, GifFile->Image.Height);

    for (i = l = 0; i < ColorMap->ColorCount; i++)
    {
        (void)snprintf(Line, sizeof(Line),
                "Color %-3d: [%-3d, %-3d, %-3d] ", i,
                ColorMap->Colors[i].Red,
                ColorMap->Colors[i].Green,
                ColorMap->Colors[i].Blue);
        GenRasterTextLine(RasterBuffer, Line, IMAGEWIDTH, i);
        for (j = 0; j < GIF_FONT_HEIGHT; j++)
        {
            if (EGifPutLine(GifFile, RasterBuffer[j], IMAGEWIDTH) == GIF_ERROR)
                QuitGifError(GifFile);
            printf("\b\b\b\b%-4d", l++);
        }
    }

    if (EGifCloseFile(GifFile, &ErrorCode) == GIF_ERROR) {
        printf("error: %d\n", ErrorCode);
        if (GifFile != NULL) {
            EGifCloseFile(GifFile, NULL);
        }
        exit(EXIT_FAILURE);
    }

    return 0;
}

/******************************************************************************
 Close output file (if open), and exit.
******************************************************************************/
static void GenRasterTextLine(GifRowType *RasterBuffer, char *TextLine,
                    int BufferWidth, int ForeGroundIndex)
{
    unsigned char c;
    unsigned char Byte, Mask;
    int i, j, k, CharPosX, Len = (int)strlen(TextLine);

    for (i = 0; i < BufferWidth; i++)
        for (j = 0; j < GIF_FONT_HEIGHT; j++)
            RasterBuffer[j][i] = BackGround;

    for (i = CharPosX = 0; i < Len; i++, CharPosX += GIF_FONT_WIDTH) {
        c = TextLine[i];
        for (j = 0; j < GIF_FONT_HEIGHT; j++) {
            Byte = GifAsciiTable8x8[(unsigned short)c][j];
            for (k = 0, Mask = 128; k < GIF_FONT_WIDTH; k++, Mask >>= 1)
            if (Byte & Mask)
                RasterBuffer[j][CharPosX + k] = ForeGroundIndex;
        }
    }
}

/******************************************************************************
 Close output file (if open), and exit.
******************************************************************************/
static void QuitGifError(GifFileType *GifFile)
{
    if (GifFile != NULL) {
        printf("error: %d\n", GifFile->Error);
        EGifCloseFile(GifFile, NULL);
    }
    exit(EXIT_FAILURE);
}
