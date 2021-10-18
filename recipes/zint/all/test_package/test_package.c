/* main.c - Command line handling routines for Zint */

/*
    libzint - the open source barcode library
    Copyright (C) 2008-2021 Robin Stuart <rstuart114@gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */
/* vim: set ts=4 sw=4 et : */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include "zint.h"
#include "getopt.h"

#ifdef _MSC_VER
#include <malloc.h>
#if _MSC_VER >= 1900 /* MSVC 2015 */
#pragma warning(disable: 4996) /* function or variable may be unsafe */
#endif /* _MSC_VER */
#endif
/* It's assumed that int is at least 32 bits, the following will compile-time fail if not
 * https://stackoverflow.com/a/1980056/664741 */
typedef int static_assert_int_at_least_32bits[CHAR_BIT != 8 || sizeof(int) < 4 ? -1 : 1];

#ifndef ARRAY_SIZE
#define ARRAY_SIZE(x) (sizeof(x) / sizeof((x)[0]))
#endif

/* Print list of supported symbologies */
static void types(void) {
    printf( " 1 CODE11      Code 11                  74 CODABLOCKF     Codablock-F\n"
            " 2 C25STANDARD Standard 2of5            75 NVE18          NVE-18\n"
            " 3 C25INTER    Interleaved 2of5         76 JAPANPOST      Japanese Post\n"
            " 4 C25IATA     IATA 2of5                77 KOREAPOST      Korea Post\n"
            " 6 C25LOGIC    Data Logic 2of5          79 DBAR_STK       GS1 DataBar Stacked\n"
            " 7 C25IND      Industrial 2of5          80 DBAR_OMNSTK    GS1 DataBar Stack Omni\n"
            " 8 CODE39      Code 39                  81 DBAR_EXPSTK    GS1 DataBar Exp Stack\n"
            " 9 EXCODE39    Extended Code 39         82 PLANET         USPS PLANET\n"
            "13 EANX        EAN                      84 MICROPDF417    MicroPDF417\n"
            "14 EANX_CHK    EAN + Check Digit        85 USPS_IMAIL     USPS Intelligent Mail\n"
            "16 GS1_128     GS1-128                  86 PLESSEY        UK Plessey\n"
            "18 CODABAR     Codabar                  87 TELEPEN_NUM    Telepen Numeric\n"
            "20 CODE128     Code 128                 89 ITF14          ITF-14\n"
            "21 DPLEIT      Deutsche Post Leitcode   90 KIX            Dutch Post KIX Code\n"
            "22 DPIDENT     Deutsche Post Identcode  92 AZTEC          Aztec Code\n"
            "23 CODE16K     Code 16k                 93 DAFT           DAFT Code\n"
            "24 CODE49      Code 49                  96 DPD            DPD Parcel Code 128\n"
            "25 CODE93      Code 93                  97 MICROQR        Micro QR Code\n"
            "28 FLAT        Flattermarken            98 HIBC_128       HIBC Code 128\n"
            "29 DBAR_OMN    GS1 DataBar Omni         99 HIBC_39        HIBC Code 39\n"
            "30 DBAR_LTD    GS1 DataBar Limited     102 HIBC_DM        HIBC Data Matrix\n"
            "31 DBAR_EXP    GS1 DataBar Expanded    104 HIBC_QR        HIBC QR Code\n"
            "32 TELEPEN     Telepen Alpha           106 HIBC_PDF       HIBC PDF417\n"
            "34 UPCA        UPC-A                   108 HIBC_MICPDF    HIBC MicroPDF417\n"
            "35 UPCA_CHK    UPC-A + Check Digit     110 HIBC_BLOCKF    HIBC Codablock-F\n"
            "37 UPCE        UPC-E                   112 HIBC_AZTEC     HIBC Aztec Code\n"
            "38 UPCE_CHK    UPC-E + Check Digit     115 DOTCODE        DotCode\n"
            "40 POSTNET     USPS POSTNET            116 HANXIN         Han Xin Code\n"
            "47 MSI_PLESSEY MSI Plessey             121 MAILMARK       Royal Mail Mailmark\n"
            "49 FIM         Facing Ident Mark       128 AZRUNE         Aztec Runes\n"
            "50 LOGMARS     LOGMARS Code 39         129 CODE32         Code 32\n"
            "51 PHARMA      Pharmacode One-Track    130 EANX_CC        Composite EAN\n"
            "52 PZN         Pharmazentralnummer     131 GS1_128_CC     Composite GS1-128\n"
            "53 PHARMA_TWO  Pharmacode Two-Track    132 DBAR_OMN_CC    Comp DataBar Omni\n"
            "55 PDF417      PDF417                  133 DBAR_LTD_CC    Comp DataBar Limited\n"
            "56 PDF417COMP  Compact PDF417          134 DBAR_EXP_CC    Comp DataBar Expanded\n"
            "57 MAXICODE    MaxiCode                135 UPCA_CC        Composite UPC-A\n"
            "58 QRCODE      QR Code                 136 UPCE_CC        Composite UPC-E\n"
            "60 CODE128B    Code 128 (Subset B)     137 DBAR_STK_CC    Comp DataBar Stacked\n"
            "63 AUSPOST     AP Standard Customer    138 DBAR_OMNSTK_CC Comp DataBar Stack Omn\n"
            "66 AUSREPLY    AP Reply Paid           139 DBAR_EXPSTK_CC Comp DataBar Exp Stack\n"
            "67 AUSROUTE    AP Routing              140 CHANNEL        Channel Code\n"
            "68 AUSREDIRECT AP Redirection          141 CODEONE        Code One\n"
            "69 ISBNX       ISBN                    142 GRIDMATRIX     Grid Matrix\n"
            "70 RM4SCC      Royal Mail 4SCC         143 UPNQR          UPN QR Code\n"
            "71 DATAMATRIX  Data Matrix             144 ULTRA          Ultracode\n"
            "72 EAN14       EAN-14                  145 RMQR           Rectangular Micro QR\n"
            "73 VIN         Vehicle Information No.\n"
            );
}

/* Output usage information */
static void usage(void) {
    int zint_version = ZBarcode_Version();
    int version_major = zint_version / 10000;
    int version_minor = (zint_version % 10000) / 100;
    int version_release = zint_version % 100;
    int version_build;
    
    if (version_release > 10) {
        /* This is a test release */
        version_release = version_release / 10;
        version_build = zint_version % 10;
        printf( "Zint version %d.%d.%d.%d\n", version_major, version_minor, version_release, version_build);
    } else {
        /* This is a stable release */
        printf( "Zint version %d.%d.%d\n", version_major, version_minor, version_release);
    }
    
    printf( "Encode input data in a barcode and save as BMP/EMF/EPS/GIF/PCX/PNG/SVG/TIF/TXT\n\n"
            "  -b, --barcode=TYPE    Number or name of barcode type. Default is 20 (CODE128)\n"
            "  --addongap=NUMBER     Set add-on gap in multiples of X-dimension for UPC/EAN\n"
            "  --batch               Treat each line of input file as a separate data set\n"
            "  --bg=COLOUR           Specify a background colour (in hex RGB/RGBA)\n"
            "  --binary              Treat input as raw binary data\n"
            "  --bind                Add boundary bars\n"
            "  --bold                Use bold text\n"
            "  --border=NUMBER       Set width of border in multiples of X-dimension\n"
            "  --box                 Add a box around the symbol\n"
            "  --cmyk                Use CMYK colour space in EPS/TIF symbols\n"
            "  --cols=NUMBER         Set the number of data columns in symbol\n"
            "  -d, --data=DATA       Set the symbol content\n"
            "  --direct              Send output to stdout\n"
            "  --dmre                Allow Data Matrix Rectangular Extended\n"
            "  --dotsize=NUMBER      Set radius of dots in dotty mode\n"
            "  --dotty               Use dots instead of squares for matrix symbols\n"
            "  --dump                Dump hexadecimal representation to stdout\n"
            "  -e, --ecinos          Display table of ECI character encodings\n"
            "  --eci=NUMBER          Set the ECI (Extended Channel Interpretation) code\n"
            "  --esc                 Process escape characters in input data\n"
            "  --fg=COLOUR           Specify a foreground colour (in hex RGB/RGBA)\n"
            "  --filetype=TYPE       Set output file type BMP/EMF/EPS/GIF/PCX/PNG/SVG/TIF/TXT\n"
            "  --fullmultibyte       Use multibyte for binary/Latin (QR/Han Xin/Grid Matrix)\n"
            "  --gs1                 Treat input as GS1 compatible data\n"
            "  --gs1parens           GS1 AIs in parentheses instead of square brackets\n"
            "  --gssep               Use separator GS for GS1 (Data Matrix)\n"
            "  -h, --help            Display help message\n"
            "  --height=NUMBER       Set height of symbol in multiples of X-dimension\n"
            "  -i, --input=FILE      Read input data from FILE\n"
            "  --init                Create reader initialisation/programming symbol\n"
            "  --mask=NUMBER         Set masking pattern to use (QR/Han Xin/DotCode)\n"
            "  --mirror              Use batch data to determine filename\n"
            "  --mode=NUMBER         Set encoding mode (MaxiCode/Composite)\n"
            "  --nobackground        Remove background (EMF/EPS/GIF/PNG/SVG/TIF only)\n"
            "  --notext              Remove human readable text\n"
            "  -o, --output=FILE     Send output to FILE. Default is out.png\n"
            "  --primary=STRING      Set structured primary message (MaxiCode/Composite)\n"
            "  -r, --reverse         Reverse colours (white on black)\n"
            "  --rotate=NUMBER       Rotate symbol by NUMBER degrees\n"
            "  --rows=NUMBER         Set number of rows (Codablock-F)\n"
            "  --scale=NUMBER        Adjust size of X-dimension\n"
            "  --scmvv=NUMBER        Prefix SCM with [)>\\R01\\Gvv (vv is NUMBER) (MaxiCode)\n"
            "  --secure=NUMBER       Set error correction level (ECC)\n"
            "  --separator=NUMBER    Set height of row separator bars (stacked symbologies)\n"
            "  --small               Use small text\n"
            "  --square              Force Data Matrix symbols to be square\n"
            "  -t, --types           Display table of barcode types\n"
            "  --vers=NUMBER         Set symbol version (size, check digits, other options)\n"
            "  --vwhitesp=NUMBER     Set height of vertical whitespace in multiples of X-dim\n"
            "  -w, --whitesp=NUMBER  Set width of horizontal whitespace in multiples of X-dim\n"
            "  --werror              Convert all warnings into errors\n"
            "  --wzpl                ZPL compatibility mode (allows non-standard symbols)\n"
            );
}

/* Display supported ECI codes */
static void show_eci(void) {
    printf( "  3: ISO/IEC 8859-1 - Latin alphabet No. 1 (default)\n"
            "  4: ISO/IEC 8859-2 - Latin alphabet No. 2\n"
            "  5: ISO/IEC 8859-3 - Latin alphabet No. 3\n"
            "  6: ISO/IEC 8859-4 - Latin alphabet No. 4\n"
            "  7: ISO/IEC 8859-5 - Latin/Cyrillic alphabet\n"
            "  8: ISO/IEC 8859-6 - Latin/Arabic alphabet\n"
            "  9: ISO/IEC 8859-7 - Latin/Greek alphabet\n"
            " 10: ISO/IEC 8859-8 - Latin/Hebrew alphabet\n"
            " 11: ISO/IEC 8859-9 - Latin alphabet No. 5 (Turkish)\n"
            " 12: ISO/IEC 8859-10 - Latin alphabet No. 6 (Nordic)\n"
            " 13: ISO/IEC 8859-11 - Latin/Thai alphabet\n"
            " 15: ISO/IEC 8859-13 - Latin alphabet No. 7 (Baltic)\n"
            " 16: ISO/IEC 8859-14 - Latin alphabet No. 8 (Celtic)\n"
            " 17: ISO/IEC 8859-15 - Latin alphabet No. 9\n"
            " 18: ISO/IEC 8859-16 - Latin alphabet No. 10\n"
            " 20: Shift JIS (JIS X 0208 and JIS X 0201)\n"
            " 21: Windows 1250 - Latin 2 (Central Europe)\n"
            " 22: Windows 1251 - Cyrillic\n"
            " 23: Windows 1252 - Latin 1\n"
            " 24: Windows 1256 - Arabic\n"
            " 25: UCS-2BE (High order byte first) (Unicode BMP)\n"
            " 26: UTF-8 (Unicode)\n"
            " 27: ISO/IEC 646:1991 7-bit character set (ASCII)\n"
            " 28: Big5 (Taiwan) Chinese Character Set\n"
            " 29: ** GB (PRC) Chinese Character Set\n"
            " 30: Korean Character Set EUC-KR (KS X 1001:2002)\n"
            "899: 8-bit binary data\n"
            "** ECI 29 is GB 2312 except for Han Xin, when it is GB 18030\n"
    );
}

/* Verifies that a string (length <= 9) only uses digits. On success returns value in arg */
static int validate_int(const char source[], int *p_val) {
    int val = 0;
    int i;
    int length = (int) strlen(source);

    if (length > 9) { /* Prevent overflow */
        return 0;
    }
    for (i = 0; i < length; i++) {
        if (source[i] < '0' || source[i] > '9') {
            return 0;
        }
        val *= 10;
        val += source[i] - '0';
    }
    *p_val = val;

    return 1;
}

/* Converts an integer value to its hexadecimal character */
static char itoc(const int source) {
    if ((source >= 0) && (source <= 9)) {
        return ('0' + source);
    } else {
        return ('A' + (source - 10));
    }
}

/* Converts upper case characters to lower case in a string source[] */
static void to_lower(char source[]) {
    int i, src_len = (int) strlen(source);

    for (i = 0; i < src_len; i++) {
        if ((source[i] >= 'A') && (source[i] <= 'Z')) {
            source[i] = (source[i] - 'A') + 'a';
        }
    }
}

/* Return symbology id if `barcode_name` a barcode name */
static int get_barcode_name(const char *barcode_name) {
    struct name { const int symbology; const char *n; };
    static const struct name names[] = { /* Must be sorted for binary search to work */
        { BARCODE_AUSPOST, "auspost" },
        { BARCODE_AUSREDIRECT, "ausredirect" },
        { BARCODE_AUSREPLY, "ausreply" },
        { BARCODE_AUSROUTE, "ausroute" },
        { BARCODE_AZRUNE, "azrune" },
        { BARCODE_AZTEC, "aztec" },
        { BARCODE_AZRUNE, "aztecrune" }, /* Synonym */
        { BARCODE_AZRUNE, "aztecrunes" }, /* Synonym */
        { BARCODE_C25IATA, "c25iata" },
        { BARCODE_C25IND, "c25ind" },
        { BARCODE_C25INTER, "c25inter" },
        { BARCODE_C25LOGIC, "c25logic" },
        { BARCODE_C25STANDARD, "c25standard" },
        { BARCODE_CHANNEL, "channel" },
        { BARCODE_CODABAR, "codabar" },
        { BARCODE_CODABLOCKF, "codablockf" },
        { BARCODE_CODE11, "code11" },
        { BARCODE_CODE128, "code128" },
        { BARCODE_CODE128B, "code128b" },
        { BARCODE_CODE16K, "code16k" },
        { BARCODE_CODE32, "code32" },
        { BARCODE_CODE39, "code39" },
        { BARCODE_CODE49, "code49" },
        { BARCODE_CODE93, "code93" },
        { BARCODE_CODEONE, "codeone" },
        { BARCODE_DAFT, "daft" },
        { BARCODE_DATAMATRIX, "datamatrix" },
        { BARCODE_DBAR_EXP, "dbarexp" },
        { BARCODE_DBAR_EXP_CC, "dbarexpcc" },
        { BARCODE_DBAR_EXPSTK, "dbarexpstk" },
        { BARCODE_DBAR_EXPSTK_CC, "dbarexpstkcc" },
        { BARCODE_DBAR_LTD, "dbarltd" },
        { BARCODE_DBAR_LTD_CC, "dbarltdcc" },
        { BARCODE_DBAR_OMN, "dbaromn" },
        { BARCODE_DBAR_OMN_CC, "dbaromncc" },
        { BARCODE_DBAR_OMNSTK, "dbaromnstk" },
        { BARCODE_DBAR_OMNSTK_CC, "dbaromnstkcc" },
        { BARCODE_DBAR_STK, "dbarstk" },
        { BARCODE_DBAR_STK_CC, "dbarstkcc" },
        { BARCODE_DOTCODE, "dotcode" },
        { BARCODE_DPD, "dpd" },
        { BARCODE_DPIDENT, "dpident" },
        { BARCODE_DPLEIT, "dpleit" },
        { BARCODE_EANX, "ean" }, /* Synonym */
        { BARCODE_EAN14, "ean14" },
        { BARCODE_EANX_CC, "eancc" }, /* Synonym */
        { BARCODE_EANX_CHK, "eanchk" }, /* Synonym */
        { BARCODE_EANX, "eanx" },
        { BARCODE_EANX_CC, "eanxcc" },
        { BARCODE_EANX_CHK, "eanxchk" },
        { BARCODE_EXCODE39, "excode39" },
        { BARCODE_FIM, "fim" },
        { BARCODE_FLAT, "flat" },
        { BARCODE_GRIDMATRIX, "gridmatrix" },
        { BARCODE_GS1_128, "gs1128" },
        { BARCODE_GS1_128_CC, "gs1128cc" },
        { BARCODE_HANXIN, "hanxin" },
        { BARCODE_HIBC_128, "hibc128" },
        { BARCODE_HIBC_39, "hibc39" },
        { BARCODE_HIBC_AZTEC, "hibcaztec" },
        { BARCODE_HIBC_BLOCKF, "hibcblockf" },
        { BARCODE_HIBC_BLOCKF, "hibccodablockf" }, /* Synonym */
        { BARCODE_HIBC_128, "hibccode128" }, /* Synonym */
        { BARCODE_HIBC_39, "hibccode39" }, /* Synonym */
        { BARCODE_HIBC_DM, "hibcdatamatrix" }, /* Synonym */
        { BARCODE_HIBC_DM, "hibcdm" },
        { BARCODE_HIBC_MICPDF, "hibcmicpdf" },
        { BARCODE_HIBC_MICPDF, "hibcmicropdf" }, /* Synonym */
        { BARCODE_HIBC_MICPDF, "hibcmicropdf417" }, /* Synonym */
        { BARCODE_HIBC_PDF, "hibcpdf" },
        { BARCODE_HIBC_PDF, "hibcpdf417" }, /* Synonym */
        { BARCODE_HIBC_QR, "hibcqr" },
        { BARCODE_HIBC_QR, "hibcqrcode" }, /* Synonym */
        { BARCODE_ISBNX, "isbnx" },
        { BARCODE_ITF14, "itf14" },
        { BARCODE_JAPANPOST, "japanpost" },
        { BARCODE_KIX, "kix" },
        { BARCODE_KOREAPOST, "koreapost" },
        { BARCODE_LOGMARS, "logmars" },
        { BARCODE_MAILMARK, "mailmark" },
        { BARCODE_MAXICODE, "maxicode" },
        { BARCODE_MICROPDF417, "micropdf417" },
        { BARCODE_MICROQR, "microqr" },
        { BARCODE_MSI_PLESSEY, "msi" }, /* Synonym */
        { BARCODE_MSI_PLESSEY, "msiplessey" },
        { BARCODE_NVE18, "nve18" },
        { BARCODE_PDF417, "pdf417" },
        { BARCODE_PDF417COMP, "pdf417comp" },
        { BARCODE_PHARMA, "pharma" },
        { BARCODE_PHARMA_TWO, "pharmatwo" },
        { BARCODE_PLANET, "planet" },
        { BARCODE_PLESSEY, "plessey" },
        { BARCODE_POSTNET, "postnet" },
        { BARCODE_PZN, "pzn" },
        { BARCODE_QRCODE, "qr" }, /* Synonym */
        { BARCODE_QRCODE, "qrcode" },
        { BARCODE_RM4SCC, "rm4scc" },
        { BARCODE_RMQR, "rmqr" },
        { BARCODE_TELEPEN, "telepen" },
        { BARCODE_TELEPEN_NUM, "telepennum" },
        { BARCODE_ULTRA, "ultra" },
        { BARCODE_ULTRA, "ultracode" }, /* Synonym */
        { BARCODE_UPCA, "upca" },
        { BARCODE_UPCA_CC, "upcacc" },
        { BARCODE_UPCA_CHK, "upcachk" },
        { BARCODE_UPCE, "upce" },
        { BARCODE_UPCE_CC, "upcecc" },
        { BARCODE_UPCE_CHK, "upcechk" },
        { BARCODE_UPNQR, "upnqr" },
        { BARCODE_UPNQR, "upnqrcode" }, /* Synonym */
        { BARCODE_USPS_IMAIL, "uspsimail" },
        { BARCODE_VIN, "vin" },
    };
    int s = 0, e = ARRAY_SIZE(names) - 1;

    char n[30] = {0};
    int i, j, length;

    /* Ignore case and any "BARCODE" prefix */
    strncpy(n, barcode_name, 29);
    to_lower(n);
    length = (int) strlen(n);
    if (strncmp(n, "barcode", 7) == 0) {
        memmove(n, n + 7, length - 7 + 1); /* Include NUL char */
        length = (int) strlen(n);
    }

    /* Ignore any non-alphanumeric characters */
    for (i = 0, j = 0; i < length; i++) {
        if ((n[i] >= 'a' && n[i] <= 'z') || (n[i] >= '0' && n[i] <= '9')) {
            n[j++] = n[i];
        }
    }
    if (j == 0) {
        return 0;
    }
    n[j] = '\0';

    while (s <= e) {
        int m = (s + e) / 2;
        int cmp = strcmp(names[m].n, n);
        if (cmp < 0) {
            s = m + 1;
        } else if (cmp > 0) {
            e = m - 1;
        } else {
            return names[m].symbology;
        }
    }

    return 0;
}

/* Whether `filetype` supported by Zint. Sets `png_refused` if `no_png` and PNG requested */
static int supported_filetype(const char *filetype, const int no_png, int *png_refused) {
    static const char *filetypes[] = {
        "bmp", "emf", "eps", "gif", "pcx", "png", "svg", "tif", "txt",
    };
    char lc_filetype[4] = {0};
    int i;

    if (png_refused) {
        *png_refused = 0;
    }
    strncpy(lc_filetype, filetype, 3);
    to_lower(lc_filetype);

    if (no_png && strcmp(lc_filetype, "png") == 0) {
        if (png_refused) {
            *png_refused = 1;
        }
        return 0;
    }

    for (i = 0; i < (int) ARRAY_SIZE(filetypes); i++) {
        if (strcmp(lc_filetype, filetypes[i]) == 0) {
            return 1;
        }
    }
    return 0;
}

/* Get file extension, excluding those of 4 or more letters */
static char *get_extension(const char *file) {
    char *dot;

    dot = strrchr(file, '.');
    if (dot && strlen(file) - (dot - file) <= 4) { /* Only recognize up to 3 letter extensions */
        return dot + 1;
    }
    return NULL;
}

/* Set extension of `file` to `filetype`, replacing existing extension if any.
 * Does nothing if file already has `filetype` extension */
static void set_extension(char *file, const char *filetype) {
    char lc_filetype[4] = {0};
    char *extension;
    char lc_extension[4];

    strncpy(lc_filetype, filetype, 3);
    to_lower(lc_filetype);

    extension = get_extension(file);
    if (extension) {
        strcpy(lc_extension, extension);
        to_lower(lc_extension);
        if (strcmp(lc_filetype, lc_extension) == 0) {
            return;
        }
        *(extension - 1) = '\0'; /* Cut off at dot */
    }
    if (strlen(file) > 251) {
        file[251] = '\0';
    }
    strcat(file, ".");
    strncat(file, filetype, 3);
}

/* Whether `filetype` is raster type */
static int is_raster(const char *filetype, const int no_png) {
    static const char *raster_filetypes[] = {
        "bmp", "gif", "pcx", "png", "tif",
    };
    int i;
    char lc_filetype[4] = {0};

    if (filetype == NULL) {
        return 0;
    }
    strcpy(lc_filetype, filetype);
    to_lower(lc_filetype);

    if (no_png && strcmp(lc_filetype, "png") == 0) {
        return 0;
    }

    for (i = 0; i < (int) ARRAY_SIZE(raster_filetypes); i++) {
        if (strcmp(lc_filetype, raster_filetypes[i]) == 0) {
            return 1;
        }
    }
    return 0;
}

/* Batch mode - output symbol for each line of text in `filename` */
static int batch_process(struct zint_symbol *symbol, const char *filename, const int mirror_mode,
            const char *filetype, const int rotate_angle) {
    FILE *file;
    unsigned char buffer[ZINT_MAX_DATA_LEN] = {0}; // Maximum HanXin input
    unsigned char character = 0;
    int buf_posn = 0, error_number = 0, line_count = 1;
    char output_file[256];
    char number[12], reverse_number[12];
    int inpos, local_line_count;
    char format_string[256], reversed_string[256], format_char;
    int format_len, i, o;
    char adjusted[2] = {0};

    if (symbol->outfile[0] == '\0') {
        strcpy(format_string, "~~~~~.");
        strncat(format_string, filetype, 3);
    } else {
        strcpy(format_string, symbol->outfile);
        set_extension(format_string, filetype);
    }

    if (!strcmp(filename, "-")) {
        file = stdin;
    } else {
        file = fopen(filename, "rb");
        if (!file) {
            strcpy(symbol->errtxt, "102: Unable to read input file");
            return ZINT_ERROR_INVALID_DATA;
        }
    }

    do {
        int intChar;
        intChar = fgetc(file);
        if (intChar == EOF) {
            break;
        }
        character = (unsigned char) intChar;
        if (character == '\n') {
            if (buf_posn > 0 && buffer[buf_posn - 1] == '\r') {
                /* CR+LF - assume Windows formatting and remove CR */
                buf_posn--;
                buffer[buf_posn] = '\0';
            }

            if (mirror_mode == 0) {
                inpos = 0;
                local_line_count = line_count;
                memset(number, 0, sizeof(number));
                memset(reverse_number, 0, sizeof(reverse_number));
                memset(reversed_string, 0, sizeof(reversed_string));
                memset(output_file, 0, sizeof(output_file));
                do {
                    number[inpos] = itoc(local_line_count % 10);
                    local_line_count /= 10;
                    inpos++;
                } while (local_line_count > 0);
                number[inpos] = '\0';

                for (i = 0; i < inpos; i++) {
                    reverse_number[i] = number[inpos - i - 1];
                }

                format_len = (int) strlen(format_string);
                for (i = format_len; i > 0; i--) {
                    format_char = format_string[i - 1];

                    switch (format_char) {
                        case '#':
                            if (inpos > 0) {
                                adjusted[0] = reverse_number[inpos - 1];
                                inpos--;
                            } else {
                                adjusted[0] = ' ';
                            }
                            break;
                        case '~':
                            if (inpos > 0) {
                                adjusted[0] = reverse_number[inpos - 1];
                                inpos--;
                            } else {
                                adjusted[0] = '0';
                            }
                            break;
                        case '@':
                            if (inpos > 0) {
                                adjusted[0] = reverse_number[inpos - 1];
                                inpos--;
                            } else {
                                adjusted[0] = '*';
                            }
                            break;
                        default:
                            adjusted[0] = format_string[i - 1];
                            break;
                    }
                    strcat(reversed_string, adjusted);
                }

                for (i = 0; i < format_len; i++) {
                    output_file[i] = reversed_string[format_len - i - 1];
                }
            } else {
                /* Name the output file from the data being processed */
                i = 0;
                o = 0;
                do {
                    if (buffer[i] < 0x20) {
                        output_file[o] = '_';
                    } else {
                        switch (buffer[i]) {
                            case 0x21: // !
                            case 0x22: // "
                            case 0x2a: // *
                            case 0x2f: // /
                            case 0x3a: // :
                            case 0x3c: // <
                            case 0x3e: // >
                            case 0x3f: // ?
                            case 0x5c: // Backslash
                            case 0x7c: // |
                            case 0x7f: // DEL
                                output_file[o] = '_';
                                break;
                            default:
                                output_file[o] = buffer[i];
                                break;
                        }
                    }

                    // Skip escape characters
                    if ((buffer[i] == 0x5c) && (symbol->input_mode & ESCAPE_MODE)) {
                        i++;
                        if (buffer[i] == 'x') {
                            i += 2;
                        } else if (buffer[i] == 'u') {
                            i += 4;
                        }
                    }
                    i++;
                    o++;
                } while (i < buf_posn && o < 251);

                /* Add file extension */
                output_file[o] = '.';
                output_file[o + 1] = '\0';

                strncat(output_file, filetype, 3);
            }

            strcpy(symbol->outfile, output_file);
            error_number = ZBarcode_Encode_and_Print(symbol, buffer, buf_posn, rotate_angle);
            if (error_number != 0) {
                fprintf(stderr, "On line %d: %s\n", line_count, symbol->errtxt);
                fflush(stderr);
            }
            ZBarcode_Clear(symbol);
            memset(buffer, 0, sizeof(buffer));
            buf_posn = 0;
            line_count++;
        } else {
            buffer[buf_posn] = character;
            buf_posn++;
        }
        if (buf_posn >= (int) sizeof(buffer)) {
            fprintf(stderr, "On line %d: Error 103: Input data too long\n", line_count);
            fflush(stderr);
            do {
                character = fgetc(file);
            } while ((!feof(file)) && (character != '\n'));
        }
    } while ((!feof(file)) && (line_count < 2000000000));

    if (character != '\n') {
        fprintf(stderr, "Warning 104: No newline at end of file\n");
        fflush(stderr);
    }

    fclose(file);
    return error_number;
}

/* Stuff to convert args on Windows command line to UTF-8 */
#ifdef _WIN32
#include <windows.h>
#include <shellapi.h>

#ifndef WC_ERR_INVALID_CHARS
#define WC_ERR_INVALID_CHARS    0x00000080
#endif

static int win_argc = 0;
static char **win_argv = NULL;

/* Free Windows args */
static void win_free_args() {
    int i;
    if (!win_argv) {
        return;
    }
    for (i = 0; i < win_argc; i++) {
        if (!win_argv[i]) {
            break;
        }
        free(win_argv[i]);
        win_argv[i] = NULL;
    }
    free(win_argv);
    win_argv = NULL;
}

/* For Windows replace args with UTF-8 versions */
static void win_args(int *p_argc, char ***p_argv) {
    int i;
    LPWSTR *szArgList = CommandLineToArgvW(GetCommandLineW(), &win_argc);
    if (szArgList) {
        if (!(win_argv = (char **) calloc(win_argc + 1, sizeof(char *)))) {
            LocalFree(szArgList);
        } else {
            for (i = 0; i < win_argc; i++) {
                int len = WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, szArgList[i], -1, NULL, 0, NULL, NULL);
                if (len == 0 || !(win_argv[i] = malloc(len + 1))) {
                    win_free_args();
                    LocalFree(szArgList);
                    return;
                }
                if (WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, szArgList[i], -1, win_argv[i], len, NULL, NULL)
                        == 0) {
                    win_free_args();
                    LocalFree(szArgList);
                    return;
                }
            }
            for (i = 0; i < win_argc; i++) {
                (*p_argv)[i] = win_argv[i];
            }
            *p_argc = win_argc;
            LocalFree(szArgList);
        }
    }
}
#endif /* _WIN32 */

/* Helper to free Windows args on exit */
static int do_exit(int error_number) {
#ifdef _WIN32
    win_free_args();
#endif
    exit(error_number);
    return error_number; /* Not reached */
}

typedef struct { char *arg; int opt; } arg_opt;

int main(int argc, char **argv) {
    struct zint_symbol *my_symbol;
    int error_number = 0;
    int rotate_angle = 0;
    int help = 0;
    int data_cnt = 0;
    int input_cnt = 0;
    int batch_mode = 0;
    int mirror_mode = 0;
    int fullmultibyte = 0;
    int mask = 0;
    int separator = 0;
    int addon_gap = 0;
    char filetype[4] = {0};
    int no_png;
    int png_refused;
    int val;
    int i;
    int ret;
    char *outfile_extension;
    int data_arg_num = 0;
#ifndef _MSC_VER
    arg_opt arg_opts[argc];
#else
    arg_opt *arg_opts = (arg_opt *) _alloca(argc * sizeof(arg_opt));
#endif

    if (argc == 1) {
        usage();
        exit(1);
    }

    my_symbol = ZBarcode_Create();
    if (!my_symbol) {
        fprintf(stderr, "Error 151: Memory failure\n");
        exit(1);
    }
    no_png = strcmp(my_symbol->outfile, "out.gif") == 0;
    my_symbol->input_mode = UNICODE_MODE;

#ifdef _WIN32
    win_args(&argc, &argv);
#endif

    while (1) {
        enum options {
            OPT_ADDONGAP = 128, OPT_BATCH, OPT_BINARY, OPT_BG, OPT_BIND, OPT_BOLD, OPT_BORDER,
            OPT_BOX, OPT_CMYK, OPT_COLS, OPT_DIRECT, OPT_DMRE, OPT_DOTSIZE, OPT_DOTTY, OPT_DUMP,
            OPT_ECI, OPT_ESC, OPT_FG, OPT_FILETYPE, OPT_FONTSIZE, OPT_FULLMULTIBYTE,
            OPT_GS1, OPT_GS1PARENS, OPT_GSSEP, OPT_HEIGHT, OPT_INIT, OPT_MIRROR, OPT_MASK, OPT_MODE,
            OPT_NOBACKGROUND, OPT_NOTEXT, OPT_PRIMARY, OPT_ROTATE, OPT_ROWS, OPT_SCALE,
            OPT_SCMVV, OPT_SECURE, OPT_SEPARATOR, OPT_SMALL, OPT_SQUARE, OPT_VERBOSE, OPT_VERS,
            OPT_VWHITESP, OPT_WERROR, OPT_WZPL,
        };
        int option_index = 0;
        static struct option long_options[] = {
            {"addongap", 1, NULL, OPT_ADDONGAP},
            {"barcode", 1, NULL, 'b'},
            {"batch", 0, NULL, OPT_BATCH},
            {"binary", 0, NULL, OPT_BINARY},
            {"bg", 1, 0, OPT_BG},
            {"bind", 0, NULL, OPT_BIND},
            {"bold", 0, NULL, OPT_BOLD},
            {"border", 1, NULL, OPT_BORDER},
            {"box", 0, NULL, OPT_BOX},
            {"cmyk", 0, NULL, OPT_CMYK},
            {"cols", 1, NULL, OPT_COLS},
            {"data", 1, NULL, 'd'},
            {"direct", 0, NULL, OPT_DIRECT},
            {"dmre", 0, NULL, OPT_DMRE},
            {"dotsize", 1, NULL, OPT_DOTSIZE},
            {"dotty", 0, NULL, OPT_DOTTY},
            {"dump", 0, NULL, OPT_DUMP},
            {"eci", 1, NULL, OPT_ECI},
            {"ecinos", 0, NULL, 'e'},
            {"esc", 0, NULL, OPT_ESC},
            {"fg", 1, 0, OPT_FG},
            {"filetype", 1, NULL, OPT_FILETYPE},
            {"fontsize", 1, NULL, OPT_FONTSIZE},
            {"fullmultibyte", 0, NULL, OPT_FULLMULTIBYTE},
            {"gs1", 0, 0, OPT_GS1},
            {"gs1parens", 0, NULL, OPT_GS1PARENS},
            {"gssep", 0, NULL, OPT_GSSEP},
            {"height", 1, NULL, OPT_HEIGHT},
            {"help", 0, NULL, 'h'},
            {"init", 0, NULL, OPT_INIT},
            {"input", 1, NULL, 'i'},
            {"mirror", 0, NULL, OPT_MIRROR},
            {"mask", 1, NULL, OPT_MASK},
            {"mode", 1, NULL, OPT_MODE},
            {"nobackground", 0, NULL, OPT_NOBACKGROUND},
            {"notext", 0, NULL, OPT_NOTEXT},
            {"output", 1, NULL, 'o'},
            {"primary", 1, NULL, OPT_PRIMARY},
            {"reverse", 0, NULL, 'r'},
            {"rotate", 1, NULL, OPT_ROTATE},
            {"rows", 1, NULL, OPT_ROWS},
            {"scale", 1, NULL, OPT_SCALE},
            {"scmvv", 1, NULL, OPT_SCMVV},
            {"secure", 1, NULL, OPT_SECURE},
            {"separator", 1, NULL, OPT_SEPARATOR},
            {"small", 0, NULL, OPT_SMALL},
            {"square", 0, NULL, OPT_SQUARE},
            {"types", 0, NULL, 't'},
            {"verbose", 0, NULL, OPT_VERBOSE}, // Currently undocumented, output some debug info
            {"vers", 1, NULL, OPT_VERS},
            {"vwhitesp", 1, NULL, OPT_VWHITESP},
            {"werror", 0, NULL, OPT_WERROR},
            {"whitesp", 1, NULL, 'w'},
            {"wzpl", 0, NULL, OPT_WZPL},
            {NULL, 0, NULL, 0}
        };
        int c = getopt_long(argc, argv, "b:d:ehi:o:rtw:", long_options, &option_index);
        if (c == -1) break;

        switch (c) {
            case OPT_ADDONGAP:
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 139: Invalid add-on gap value (digits only)\n");
                    return do_exit(1);
                }
                if (val >= 7 && val <= 12) {
                    addon_gap = val;
                } else {
                    fprintf(stderr, "Warning 140: Add-on gap out of range (7 to 12), ignoring\n");
                    fflush(stderr);
                }
                break;
            case OPT_BATCH:
                if (data_cnt == 0) {
                    /* Switch to batch processing mode */
                    batch_mode = 1;
                } else {
                    fprintf(stderr, "Warning 141: Can't use batch mode if data given, ignoring\n");
                    fflush(stderr);
                }
                break;
            case OPT_BG:
                strncpy(my_symbol->bgcolour, optarg, 9);
                break;
            case OPT_BINARY:
                my_symbol->input_mode = (my_symbol->input_mode & ~0x07) | DATA_MODE;
                break;
            case OPT_BIND:
                my_symbol->output_options |= BARCODE_BIND;
                break;
            case OPT_BOLD:
                my_symbol->output_options |= BOLD_TEXT;
                break;
            case OPT_BORDER:
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 107: Invalid border width value (digits only)\n");
                    return do_exit(1);
                }
                if (val <= 1000) { /* `val` >= 0 always */
                    my_symbol->border_width = val;
                } else {
                    fprintf(stderr, "Warning 108: Border width out of range (0 to 1000), ignoring\n");
                    fflush(stderr);
                }
                break;
            case OPT_BOX:
                my_symbol->output_options |= BARCODE_BOX;
                break;
            case OPT_CMYK:
                my_symbol->output_options |= CMYK_COLOUR;
                break;
            case OPT_COLS:
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 131: Invalid columns value (digits only)\n");
                    return do_exit(1);
                }
                if ((val >= 1) && (val <= 200)) {
                    my_symbol->option_2 = val;
                } else {
                    fprintf(stderr, "Warning 111: Number of columns out of range (1 to 200), ignoring\n");
                    fflush(stderr);
                }
                break;
            case OPT_DIRECT:
                my_symbol->output_options |= BARCODE_STDOUT;
                break;
            case OPT_DMRE:
                /* Square overwrites DMRE */
                if (my_symbol->option_3 != DM_SQUARE) {
                    my_symbol->option_3 = DM_DMRE;
                }
                break;
            case OPT_DOTSIZE:
                my_symbol->dot_size = (float) (atof(optarg));
                if (my_symbol->dot_size < 0.01f) {
                    /* Zero and negative values are not permitted */
                    fprintf(stderr, "Warning 106: Invalid dot radius value (less than 0.01), ignoring\n");
                    fflush(stderr);
                    my_symbol->dot_size = 4.0f / 5.0f;
                }
                break;
            case OPT_DOTTY:
                my_symbol->output_options |= BARCODE_DOTTY_MODE;
                break;
            case OPT_DUMP:
                my_symbol->output_options |= BARCODE_STDOUT;
                strcpy(my_symbol->outfile, "dummy.txt");
                break;
            case OPT_ECI:
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 138: Invalid ECI value (digits only)\n");
                    return do_exit(1);
                }
                if (val <= 999999) { /* `val` >= 0 always */
                    my_symbol->eci = val;
                } else {
                    fprintf(stderr, "Warning 118: ECI code out of range (0 to 999999), ignoring\n");
                    fflush(stderr);
                }
                break;
            case OPT_ESC:
                my_symbol->input_mode |= ESCAPE_MODE;
                break;
            case OPT_FG:
                strncpy(my_symbol->fgcolour, optarg, 9);
                break;
            case OPT_FILETYPE:
                /* Select the type of output file */
                if (!supported_filetype(optarg, no_png, &png_refused)) {
                    if (png_refused) {
                        fprintf(stderr, "Warning 152: PNG format disabled at compile time, ignoring\n");
                    } else {
                        fprintf(stderr, "Warning 142: File type '%s' not supported, ignoring\n", optarg);
                    }
                    fflush(stderr);
                } else {
                    strncpy(filetype, optarg, (size_t) 3);
                }
                break;
            case OPT_FONTSIZE:
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 130: Invalid font size value (digits only)\n");
                    return do_exit(1);
                }
                if (val <= 100) { /* `val` >= 0 always */
                    my_symbol->fontsize = val;
                } else {
                    fprintf(stderr, "Warning 126: Font size out of range (0 to 100), ignoring\n");
                    fflush(stderr);
                }
                break;
            case OPT_FULLMULTIBYTE:
                fullmultibyte = 1;
                break;
            case OPT_GS1:
                my_symbol->input_mode = (my_symbol->input_mode & ~0x07) | GS1_MODE;
                break;
            case OPT_GS1PARENS:
                my_symbol->input_mode |= GS1PARENS_MODE;
                break;
            case OPT_GSSEP:
                my_symbol->output_options |= GS1_GS_SEPARATOR;
                break;
            case OPT_HEIGHT:
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 109: Invalid symbol height value (digits only)\n");
                    return do_exit(1);
                }
                if ((val >= 1) && (val <= 1000)) {
                    my_symbol->height = val;
                } else {
                    fprintf(stderr, "Warning 110: Symbol height out of range (1 to 1000), ignoring\n");
                    fflush(stderr);
                }
                break;
            case OPT_INIT:
                my_symbol->output_options |= READER_INIT;
                break;
            case OPT_MIRROR:
                /* Use filenames which reflect content */
                mirror_mode = 1;
                break;
            case OPT_MASK:
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 148: Invalid mask value (digits only)\n");
                    return do_exit(1);
                }
                if (val > 7) { /* `val` >= 0 always */
                    /* mask pattern >= 0 and <= 7 (i.e. values >= 1 and <= 8) only permitted */
                    fprintf(stderr, "Warning 147: Mask value out of range (0 to 7), ignoring\n");
                    fflush(stderr);
                } else {
                    mask = val + 1;
                }
                break;
            case OPT_MODE:
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 136: Invalid mode value (digits only)\n");
                    return do_exit(1);
                }
                if (val <= 6) { /* `val` >= 0 always */
                    my_symbol->option_1 = val;
                } else {
                    fprintf(stderr, "Warning 116: Mode value out of range (0 to 6), ignoring\n");
                    fflush(stderr);
                }
                break;
            case OPT_NOBACKGROUND:
                strcpy(my_symbol->bgcolour, "ffffff00");
                break;
            case OPT_NOTEXT:
                my_symbol->show_hrt = 0;
                break;
            case OPT_PRIMARY:
                if (strlen(optarg) <= 127) {
                    strcpy(my_symbol->primary, optarg);
                } else {
                    fprintf(stderr, "Warning 115: Primary data string too long (127 character maximum), ignoring\n");
                    fflush(stderr);
                }
                break;
            case OPT_ROTATE:
                /* Only certain inputs allowed */
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 117: Invalid rotation value (digits only)\n");
                    return do_exit(1);
                }
                switch (val) {
                    case 90: rotate_angle = 90;
                        break;
                    case 180: rotate_angle = 180;
                        break;
                    case 270: rotate_angle = 270;
                        break;
                    case 0: rotate_angle = 0;
                        break;
                    default:
                        fprintf(stderr,
                                "Warning 137: Invalid rotation parameter (0, 90, 180 or 270 only), ignoring\n");
                        fflush(stderr);
                        break;
                }
                break;
            case OPT_ROWS:
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 132: Invalid rows value (digits only)\n");
                    return do_exit(1);
                }
                if ((val >= 1) && (val <= 44)) {
                    my_symbol->option_1 = val;
                } else {
                    fprintf(stderr, "Warning 112: Number of rows out of range (1 to 44), ignoring\n");
                    fflush(stderr);
                }
                break;
            case OPT_SCALE:
                my_symbol->scale = (float) (atof(optarg));
                if (my_symbol->scale < 0.01f) {
                    /* Zero and negative values are not permitted */
                    fprintf(stderr, "Warning 105: Invalid scale value (less than 0.01), ignoring\n");
                    fflush(stderr);
                    my_symbol->scale = 1.0f;
                }
                break;
            case OPT_SCMVV:
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 149: Invalid Structured Carrier Message version value (digits only)\n");
                    return do_exit(1);
                }
                if (val <= 99) { /* `val` >= 0 always */
                    my_symbol->option_2 = val + 1;
                } else {
                    /* Version 00-99 only */
                    fprintf(stderr,
                            "Warning 150: Structured Carrier Message version out of range (0 to 99), ignoring\n");
                    fflush(stderr);
                }
                break;
            case OPT_SECURE:
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 134: Invalid ECC value (digits only)\n");
                    return do_exit(1);
                }
                if (val <= 8) { /* `val` >= 0 always */
                    my_symbol->option_1 = val;
                } else {
                    fprintf(stderr, "Warning 114: ECC level out of range (0 to 8), ignoring\n");
                    fflush(stderr);
                }
                break;
            case OPT_SEPARATOR:
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 128: Invalid separator value (digits only)\n");
                    return do_exit(1);
                }
                if (val <= 4) { /* `val` >= 0 always */
                    separator = val;
                } else {
                    /* Greater than 4 values are not permitted */
                    fprintf(stderr, "Warning 127: Separator value out of range (0 to 4), ignoring\n");
                    fflush(stderr);
                }
                break;
            case OPT_SMALL:
                my_symbol->output_options |= SMALL_TEXT;
                break;
            case OPT_SQUARE:
                my_symbol->option_3 = DM_SQUARE;
                break;
            case OPT_VERBOSE:
                my_symbol->debug = 1;
                break;
            case OPT_VERS:
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 133: Invalid version value (digits only)\n");
                    return do_exit(1);
                }
                if ((val >= 1) && (val <= 84)) {
                    my_symbol->option_2 = val;
                } else {
                    fprintf(stderr, "Warning 113: Version value out of range (1 to 84), ignoring\n");
                    fflush(stderr);
                }
                break;
            case OPT_VWHITESP:
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 153: Invalid vertical whitespace value '%s' (digits only)\n", optarg);
                    return do_exit(1);
                }
                if (val <= 1000) { /* `val` >= 0 always */
                    my_symbol->whitespace_height = val;
                } else {
                    fprintf(stderr, "Warning 154: Vertical whitespace value out of range (0 to 1000), ignoring\n");
                    fflush(stderr);
                }
                break;
            case OPT_WERROR:
                my_symbol->warn_level = WARN_FAIL_ALL;
                break;
            case OPT_WZPL:
                my_symbol->warn_level = GS1NOCHECK_MODE ;
                break;

            case 'h':
                usage();
                help = 1;
                break;

            case 't':
                types();
                help = 1;
                break;

            case 'e':
                show_eci();
                help = 1;
                break;

            case 'b':
                if (!validate_int(optarg, &val) && !(val = get_barcode_name(optarg))) {
                    fprintf(stderr, "Error 119: Invalid barcode type '%s'\n", optarg);
                    return do_exit(1);
                }
                my_symbol->symbology = val;
                break;

            case 'w':
                if (!validate_int(optarg, &val)) {
                    fprintf(stderr, "Error 120: Invalid horizontal whitespace value '%s' (digits only)\n", optarg);
                    return do_exit(1);
                }
                if (val <= 1000) { /* `val` >= 0 always */
                    my_symbol->whitespace_width = val;
                } else {
                    fprintf(stderr, "Warning 121: Horizontal whitespace value out of range (0 to 1000), ignoring\n");
                    fflush(stderr);
                }
                break;

            case 'd': /* we have some data! */
                if (batch_mode == 0) {
                    arg_opts[data_arg_num].arg = optarg;
                    arg_opts[data_arg_num].opt = c;
                    data_arg_num++;
                    data_cnt++;
                } else {
                    fprintf(stderr, "Warning 122: Can't define data in batch mode, ignoring '%s'\n", optarg);
                    fflush(stderr);
                }
                break;

            case 'i': /* Take data from file */
                if (batch_mode == 0 || input_cnt == 0) {
                    arg_opts[data_arg_num].arg = optarg;
                    arg_opts[data_arg_num].opt = c;
                    data_arg_num++;
                    input_cnt++;
                } else {
                    fprintf(stderr, "Warning 143: Can only define one input file in batch mode, ignoring '%s'\n",
                        optarg);
                    fflush(stderr);
                }
                break;

            case 'o':
                strncpy(my_symbol->outfile, optarg, 255);
                break;

            case 'r':
                strcpy(my_symbol->fgcolour, "ffffff");
                strcpy(my_symbol->bgcolour, "000000");
                break;

            case '?':
                break;

            default:
                fprintf(stderr, "Error 123: ?? getopt error 0%o\n", c);
                fflush(stderr);
                break;
        }
    }

    if (optind < argc) {
        fprintf(stderr, "Error 125: Invalid option\n");
        while (optind < argc)
            fprintf(stderr, "%s", argv[optind++]);
        fprintf(stderr, "\n");
        fflush(stderr);
    }

    if (data_arg_num) {
        unsigned int cap = ZBarcode_Cap(my_symbol->symbology, ZINT_CAP_STACKABLE | ZINT_CAP_EXTENDABLE |
                            ZINT_CAP_FULL_MULTIBYTE | ZINT_CAP_MASK);
        if (fullmultibyte && (cap & ZINT_CAP_FULL_MULTIBYTE)) {
            my_symbol->option_3 = ZINT_FULL_MULTIBYTE;
        }
        if (mask && (cap & ZINT_CAP_MASK)) {
            my_symbol->option_3 |= mask << 8;
        }
        if (separator && (cap & ZINT_CAP_STACKABLE)) {
            my_symbol->option_3 = separator;
        }
        if (addon_gap && (cap & ZINT_CAP_EXTENDABLE)) {
            my_symbol->option_2 = addon_gap;
        }

        if (batch_mode) {
            /* Take each line of text as a separate data set */
            if (data_arg_num > 1) {
                fprintf(stderr, "Warning 144: Processing first input file '%s' only\n", arg_opts[0].arg);
                fflush(stderr);
            }
            if (filetype[0] == '\0') {
                outfile_extension = get_extension(my_symbol->outfile);
                if (outfile_extension && supported_filetype(outfile_extension, no_png, NULL)) {
                    strcpy(filetype, outfile_extension);
                } else {
                    strcpy(filetype, no_png ? "gif" : "png");
                }
            }
            if (((my_symbol->symbology != BARCODE_MAXICODE && my_symbol->scale < 0.5f) || my_symbol->scale < 0.2f)
                    && is_raster(filetype, no_png)) {
                const int min = my_symbol->symbology != BARCODE_MAXICODE ? 5 : 2;
                fprintf(stderr, "Warning 145: Scaling less than 0.%d will be set to 0.%d for '%s' output\n", min, min,
                    filetype);
                fflush(stderr);
            }
            error_number = batch_process(my_symbol, arg_opts[0].arg, mirror_mode, filetype, rotate_angle);
            if (error_number != 0) {
                fprintf(stderr, "%s\n", my_symbol->errtxt);
                fflush(stderr);
            }
        } else {
            if (filetype[0] != '\0') {
                set_extension(my_symbol->outfile, filetype);
            }
            if (((my_symbol->symbology != BARCODE_MAXICODE && my_symbol->scale < 0.5f) || my_symbol->scale < 0.2f)
                    && is_raster(get_extension(my_symbol->outfile), no_png)) {
                const int min = my_symbol->symbology != BARCODE_MAXICODE ? 5 : 2;
                fprintf(stderr, "Warning 146: Scaling less than 0.%d will be set to 0.%d for '%s' output\n", min, min,
                    get_extension(my_symbol->outfile));
                fflush(stderr);
            }
            for (i = 0; i < data_arg_num; i++) {
                if (arg_opts[i].opt == 'd') {
                    ret = ZBarcode_Encode(my_symbol, (unsigned char *) arg_opts[i].arg,
                            (int) strlen(arg_opts[i].arg));
                } else {
                    ret = ZBarcode_Encode_File(my_symbol, arg_opts[i].arg);
                }
                if (ret != 0) {
                    fprintf(stderr, "%s\n", my_symbol->errtxt);
                    fflush(stderr);
                    if (error_number < ZINT_ERROR) {
                        error_number = ret;
                    }
                }
            }
            if (error_number < ZINT_ERROR) {
                error_number = ZBarcode_Print(my_symbol, rotate_angle);

                if (error_number != 0) {
                    fprintf(stderr, "%s\n", my_symbol->errtxt);
                    fflush(stderr);
                }
            }
        }
    } else if (help == 0) {
        fprintf(stderr, "Warning 124: No data received, no symbol generated\n");
        fflush(stderr);
    }

    ZBarcode_Delete(my_symbol);

    return do_exit(error_number);
}
