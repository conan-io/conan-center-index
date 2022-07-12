/******************************************************************************
 
gif_lib.h - service library for decoding and encoding GIF images
                                                                             
*****************************************************************************/

#ifndef _GIF_LIB_H_
#define _GIF_LIB_H_ 1

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

#ifdef _MSC_VER
  #ifdef USE_GIF_LIB
    #define GIF_EXPORT
  #else /* USE_GIF_LIB */
    #ifdef USE_GIF_DLL
      #define GIF_EXPORT __declspec(dllimport)
    #else /* USE_GIF_DLL */
      #define GIF_EXPORT __declspec(dllexport)
    #endif /* USE_GIF_DLL */
  #endif /* USE_GIF_LIB */
#endif /* _MSC_VER */

#define GIFLIB_MAJOR @GIFLIB_MAJOR@
#define GIFLIB_MINOR @GIFLIB_MINOR@
#define GIFLIB_RELEASE @GIFLIB_RELEASE@

#define GIF_ERROR   0
#define GIF_OK      1

#include <stddef.h>


#ifdef _MSC_VER
    #if (_MSC_VER >= 1800)
        /* C99 is not supported for MSVC vefore VS2013 */
        #include <stdbool.h>
    #else
        #ifndef __cplusplus
        typedef int bool;
        #define false 0
        #define true 1
        #endif
    #endif

    #if (_MSC_VER < 1900)
       #define snprintf _snprintf
    #endif
#endif


#define GIF_STAMP "GIFVER"          /* First chars in file - GIF stamp.  */
#define GIF_STAMP_LEN sizeof(GIF_STAMP) - 1
#define GIF_VERSION_POS 3           /* Version first character in stamp. */
#define GIF87_STAMP "GIF87a"        /* First chars in file - GIF stamp.  */
#define GIF89_STAMP "GIF89a"        /* First chars in file - GIF stamp.  */

typedef unsigned char GifPixelType;
typedef unsigned char *GifRowType;
typedef unsigned char GifByteType;
typedef unsigned int GifPrefixType;
typedef int GifWord;

typedef struct GifColorType {
    GifByteType Red, Green, Blue;
} GifColorType;

typedef struct ColorMapObject {
    int ColorCount;
    int BitsPerPixel;
    bool SortFlag;
    GifColorType *Colors;    /* on malloc(3) heap */
} ColorMapObject;

typedef struct GifImageDesc {
    GifWord Left, Top, Width, Height;   /* Current image dimensions. */
    bool Interlace;                     /* Sequential/Interlaced lines. */
    ColorMapObject *ColorMap;           /* The local color map */
} GifImageDesc;

typedef struct ExtensionBlock {
    int ByteCount;
    GifByteType *Bytes; /* on malloc(3) heap */
    int Function;       /* The block function code */
#define CONTINUE_EXT_FUNC_CODE    0x00    /* continuation subblock */
#define COMMENT_EXT_FUNC_CODE     0xfe    /* comment */
#define GRAPHICS_EXT_FUNC_CODE    0xf9    /* graphics control (GIF89) */
#define PLAINTEXT_EXT_FUNC_CODE   0x01    /* plaintext */
#define APPLICATION_EXT_FUNC_CODE 0xff    /* application block */
} ExtensionBlock;

typedef struct SavedImage {
    GifImageDesc ImageDesc;
    GifByteType *RasterBits;         /* on malloc(3) heap */
    int ExtensionBlockCount;         /* Count of extensions before image */    
    ExtensionBlock *ExtensionBlocks; /* Extensions before image */    
} SavedImage;

typedef struct GifFileType {
    GifWord SWidth, SHeight;         /* Size of virtual canvas */
    GifWord SColorResolution;        /* How many colors can we generate? */
    GifWord SBackGroundColor;        /* Background color for virtual canvas */
    GifByteType AspectByte;	     /* Used to compute pixel aspect ratio */
    ColorMapObject *SColorMap;       /* Global colormap, NULL if nonexistent. */
    int ImageCount;                  /* Number of current image (both APIs) */
    GifImageDesc Image;              /* Current image (low-level API) */
    SavedImage *SavedImages;         /* Image sequence (high-level API) */
    int ExtensionBlockCount;         /* Count extensions past last image */
    ExtensionBlock *ExtensionBlocks; /* Extensions past last image */    
    int Error;			     /* Last error condition reported */
    void *UserData;                  /* hook to attach user data (TVT) */
    void *Private;                   /* Don't mess with this! */
} GifFileType;

#define GIF_ASPECT_RATIO(n)	((n)+15.0/64.0)

typedef enum {
    UNDEFINED_RECORD_TYPE,
    SCREEN_DESC_RECORD_TYPE,
    IMAGE_DESC_RECORD_TYPE, /* Begin with ',' */
    EXTENSION_RECORD_TYPE,  /* Begin with '!' */
    TERMINATE_RECORD_TYPE   /* Begin with ';' */
} GifRecordType;

/* func type to read gif data from arbitrary sources (TVT) */
typedef int (*InputFunc) (GifFileType *, GifByteType *, int);

/* func type to write gif data to arbitrary targets.
 * Returns count of bytes written. (MRB)
 */
typedef int (*OutputFunc) (GifFileType *, const GifByteType *, int);

/******************************************************************************
 GIF89 structures
******************************************************************************/

typedef struct GraphicsControlBlock {
    int DisposalMode;
#define DISPOSAL_UNSPECIFIED      0       /* No disposal specified. */
#define DISPOSE_DO_NOT            1       /* Leave image in place */
#define DISPOSE_BACKGROUND        2       /* Set area too background color */
#define DISPOSE_PREVIOUS          3       /* Restore to previous content */
    bool UserInputFlag;      /* User confirmation required before disposal */
    int DelayTime;           /* pre-display delay in 0.01sec units */
    int TransparentColor;    /* Palette index for transparency, -1 if none */
#define NO_TRANSPARENT_COLOR	-1
} GraphicsControlBlock;

/******************************************************************************
 GIF encoding routines
******************************************************************************/

/* Main entry points */
GIF_EXPORT GifFileType *EGifOpenFileName(const char *GifFileName,
                              const bool GifTestExistence, int *Error);
GIF_EXPORT GifFileType *EGifOpenFileHandle(const int GifFileHandle, int *Error);
GIF_EXPORT GifFileType *EGifOpen(void *userPtr, OutputFunc writeFunc, int *Error);
GIF_EXPORT int EGifSpew(GifFileType * GifFile);
GIF_EXPORT const char *EGifGetGifVersion(GifFileType *GifFile); /* new in 5.x */
GIF_EXPORT int EGifCloseFile(GifFileType *GifFile, int *ErrorCode);

#define E_GIF_SUCCEEDED          0
#define E_GIF_ERR_OPEN_FAILED    1    /* And EGif possible errors. */
#define E_GIF_ERR_WRITE_FAILED   2
#define E_GIF_ERR_HAS_SCRN_DSCR  3
#define E_GIF_ERR_HAS_IMAG_DSCR  4
#define E_GIF_ERR_NO_COLOR_MAP   5
#define E_GIF_ERR_DATA_TOO_BIG   6
#define E_GIF_ERR_NOT_ENOUGH_MEM 7
#define E_GIF_ERR_DISK_IS_FULL   8
#define E_GIF_ERR_CLOSE_FAILED   9
#define E_GIF_ERR_NOT_WRITEABLE  10

/* These are legacy.  You probably do not want to call them directly */
GIF_EXPORT int EGifPutScreenDesc(GifFileType *GifFile,
                      const int GifWidth, const int GifHeight, 
		      const int GifColorRes,
                      const int GifBackGround,
                      const ColorMapObject *GifColorMap);
GIF_EXPORT int EGifPutImageDesc(GifFileType *GifFile, 
		     const int GifLeft, const int GifTop,
                     const int GifWidth, const int GifHeight, 
		     const bool GifInterlace,
                     const ColorMapObject *GifColorMap);
GIF_EXPORT void EGifSetGifVersion(GifFileType *GifFile, const bool gif89);
GIF_EXPORT int EGifPutLine(GifFileType *GifFile, GifPixelType *GifLine,
                int GifLineLen);
GIF_EXPORT int EGifPutPixel(GifFileType *GifFile, const GifPixelType GifPixel);
GIF_EXPORT int EGifPutComment(GifFileType *GifFile, const char *GifComment);
GIF_EXPORT int EGifPutExtensionLeader(GifFileType *GifFile, const int GifExtCode);
GIF_EXPORT int EGifPutExtensionBlock(GifFileType *GifFile,
                         const int GifExtLen, const void *GifExtension);
GIF_EXPORT int EGifPutExtensionTrailer(GifFileType *GifFile);
GIF_EXPORT int EGifPutExtension(GifFileType *GifFile, const int GifExtCode, 
		     const int GifExtLen,
                     const void *GifExtension);
GIF_EXPORT int EGifPutCode(GifFileType *GifFile, int GifCodeSize,
                const GifByteType *GifCodeBlock);
GIF_EXPORT int EGifPutCodeNext(GifFileType *GifFile,
                    const GifByteType *GifCodeBlock);

/******************************************************************************
 GIF decoding routines
******************************************************************************/

/* Main entry points */
GIF_EXPORT GifFileType *DGifOpenFileName(const char *GifFileName, int *Error);
GIF_EXPORT GifFileType *DGifOpenFileHandle(int GifFileHandle, int *Error);
GIF_EXPORT int DGifSlurp(GifFileType * GifFile);
GIF_EXPORT GifFileType *DGifOpen(void *userPtr, InputFunc readFunc, int *Error);    /* new one (TVT) */
    int DGifCloseFile(GifFileType * GifFile, int *ErrorCode);

#define D_GIF_SUCCEEDED          0
#define D_GIF_ERR_OPEN_FAILED    101    /* And DGif possible errors. */
#define D_GIF_ERR_READ_FAILED    102
#define D_GIF_ERR_NOT_GIF_FILE   103
#define D_GIF_ERR_NO_SCRN_DSCR   104
#define D_GIF_ERR_NO_IMAG_DSCR   105
#define D_GIF_ERR_NO_COLOR_MAP   106
#define D_GIF_ERR_WRONG_RECORD   107
#define D_GIF_ERR_DATA_TOO_BIG   108
#define D_GIF_ERR_NOT_ENOUGH_MEM 109
#define D_GIF_ERR_CLOSE_FAILED   110
#define D_GIF_ERR_NOT_READABLE   111
#define D_GIF_ERR_IMAGE_DEFECT   112
#define D_GIF_ERR_EOF_TOO_SOON   113

/* These are legacy.  You probably do not want to call them directly */
GIF_EXPORT int DGifGetScreenDesc(GifFileType *GifFile);
GIF_EXPORT int DGifGetRecordType(GifFileType *GifFile, GifRecordType *GifType);
GIF_EXPORT int DGifGetImageDesc(GifFileType *GifFile);
GIF_EXPORT int DGifGetLine(GifFileType *GifFile, GifPixelType *GifLine, int GifLineLen);
GIF_EXPORT int DGifGetPixel(GifFileType *GifFile, GifPixelType GifPixel);
GIF_EXPORT int DGifGetComment(GifFileType *GifFile, char *GifComment);
GIF_EXPORT int DGifGetExtension(GifFileType *GifFile, int *GifExtCode,
                     GifByteType **GifExtension);
GIF_EXPORT int DGifGetExtensionNext(GifFileType *GifFile, GifByteType **GifExtension);
GIF_EXPORT int DGifGetCode(GifFileType *GifFile, int *GifCodeSize,
                GifByteType **GifCodeBlock);
GIF_EXPORT int DGifGetCodeNext(GifFileType *GifFile, GifByteType **GifCodeBlock);
GIF_EXPORT int DGifGetLZCodes(GifFileType *GifFile, int *GifCode);


/******************************************************************************
 Color table quantization (deprecated)
******************************************************************************/
GIF_EXPORT int GifQuantizeBuffer(unsigned int Width, unsigned int Height,
                   int *ColorMapSize, GifByteType * RedInput,
                   GifByteType * GreenInput, GifByteType * BlueInput,
                   GifByteType * OutputBuffer,
                   GifColorType * OutputColorMap);

/******************************************************************************
 Error handling and reporting.
******************************************************************************/
GIF_EXPORT  const char *GifErrorString(int ErrorCode);     /* new in 2012 - ESR */

/*****************************************************************************
 Everything below this point is new after version 1.2, supporting `slurp
 mode' for doing I/O in two big belts with all the image-bashing in core.
******************************************************************************/

/******************************************************************************
 Color map handling from gif_alloc.c
******************************************************************************/

GIF_EXPORT  ColorMapObject *GifMakeMapObject(int ColorCount,
                                     const GifColorType *ColorMap);
GIF_EXPORT  void GifFreeMapObject(ColorMapObject *Object);
GIF_EXPORT  ColorMapObject *GifUnionColorMap(const ColorMapObject *ColorIn1,
                                     const ColorMapObject *ColorIn2,
                                     GifPixelType ColorTransIn2[]);
GIF_EXPORT  int GifBitSize(int n);

GIF_EXPORT  void *
reallocarray(void *optr, size_t nmemb, size_t size);

/******************************************************************************
 Support for the in-core structures allocation (slurp mode).              
******************************************************************************/

GIF_EXPORT  void GifApplyTranslation(SavedImage *Image, GifPixelType Translation[]);
GIF_EXPORT  int GifAddExtensionBlock(int *ExtensionBlock_Count,
				ExtensionBlock **ExtensionBlocks, 
				int Function, 
				unsigned int Len, unsigned char ExtData[]);
GIF_EXPORT  void GifFreeExtensions(int *ExtensionBlock_Count,
			      ExtensionBlock **ExtensionBlocks);
GIF_EXPORT  SavedImage *GifMakeSavedImage(GifFileType *GifFile,
                                  const SavedImage *CopyFrom);
GIF_EXPORT  void GifFreeSavedImages(GifFileType *GifFile);

/******************************************************************************
 5.x functions for GIF89 graphics control blocks
******************************************************************************/

GIF_EXPORT int DGifExtensionToGCB(const size_t GifExtensionLength,
		       const GifByteType *GifExtension,
		       GraphicsControlBlock *GCB);
GIF_EXPORT size_t EGifGCBToExtension(const GraphicsControlBlock *GCB,
		       GifByteType *GifExtension);

GIF_EXPORT int DGifSavedExtensionToGCB(GifFileType *GifFile, 
			    int ImageIndex, 
			    GraphicsControlBlock *GCB);
GIF_EXPORT int EGifGCBToSavedExtension(const GraphicsControlBlock *GCB, 
			    GifFileType *GifFile, 
			    int ImageIndex);

/******************************************************************************
 The library's internal utility font                          
******************************************************************************/

#define GIF_FONT_WIDTH  8
#define GIF_FONT_HEIGHT 8
GIF_EXPORT extern const unsigned char GifAsciiTable8x8[][GIF_FONT_WIDTH];

GIF_EXPORT void GifDrawText8x8(SavedImage *Image,
                     const int x, const int y,
                     const char *legend, const int color);

GIF_EXPORT void GifDrawBox(SavedImage *Image,
                    const int x, const int y,
                    const int w, const int d, const int color);

GIF_EXPORT void GifDrawRectangle(SavedImage *Image,
                   const int x, const int y,
                   const int w, const int d, const int color);

GIF_EXPORT void GifDrawBoxedText8x8(SavedImage *Image,
                          const int x, const int y,
                          const char *legend,
                          const int border, const int bg, const int fg);

#ifdef __cplusplus
}
#endif /* __cplusplus */
#endif /* _GIF_LIB_H */

/* end */
