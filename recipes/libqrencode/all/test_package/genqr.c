#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#include "png.h"
#include "qrencode.h"
#include "genqr.h"

#define INCHES_PER_METER (100.0/2.54)

enum imageType {
	PNG_TYPE,
	PNG32_TYPE,
};

static int casesensitive = 1;
static int eightbit = 0;
static int version = 0;
static int size = 10;
static int margin = 1;
static int dpi = 96;
static int structured = 0;
static int rle = 0;
static int svg_path = 0;
static int micro = 0;
static QRecLevel level = QR_ECLEVEL_L;
static QRencodeMode hint = QR_MODE_8;
static unsigned char fg_color[4] = { 0, 0, 0, 255 };
static unsigned char bg_color[4] = { 255, 255, 255, 255 };

static int verbose = 0;
static void fillRow(unsigned char *row, int num, const unsigned char color[])
{
	int i;

	for (i = 0; i < num; i++) {
		memcpy(row, color, 4);
		row += 4;
	}
}

static int writePNG(const QRcode *qrcode, const char *outfile, enum imageType type)
{
	static FILE *fp; // avoid clobbering by setjmp.
	png_structp png_ptr;
	png_infop info_ptr;
	png_colorp palette = NULL;
	png_byte alpha_values[2];
	unsigned char *row, *p, *q;
	int x, y, xx, yy, bit;
	int realwidth;

	realwidth = (qrcode->width + margin * 2) * size;
	if (type == PNG_TYPE) {
		row = (unsigned char *)malloc((realwidth + 7) / 8);
	}
	else if (type == PNG32_TYPE) {
		row = (unsigned char *)malloc(realwidth * 4);
	}
	else {
		fprintf(stderr, "Internal error.\n");
		return 1;
	}
	if (row == NULL) {
		fprintf(stderr, "Failed to allocate memory.\n");
		return 1;
	}

	if (outfile[0] == '-' && outfile[1] == '\0') {
		fp = stdout;
	}
	else {
		fp = fopen(outfile, "wb");
		if (fp == NULL) {
			fprintf(stderr, "Failed to create file: %s\n", outfile);
			perror(NULL);
			return 1;
		}
	}

	png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
	if (png_ptr == NULL) {
		fprintf(stderr, "Failed to initialize PNG writer.\n");
		return 1;
	}

	info_ptr = png_create_info_struct(png_ptr);
	if (info_ptr == NULL) {
		fprintf(stderr, "Failed to initialize PNG write.\n");
		return 1;
	}

	if (setjmp(png_jmpbuf(png_ptr))) {
		png_destroy_write_struct(&png_ptr, &info_ptr);
		fprintf(stderr, "Failed to write PNG image.\n");
		return 1;
	}

	if (type == PNG_TYPE) {
		palette = (png_colorp)malloc(sizeof(png_color) * 2);
		if (palette == NULL) {
			fprintf(stderr, "Failed to allocate memory.\n");
			return 1;
		}
		palette[0].red = fg_color[0];
		palette[0].green = fg_color[1];
		palette[0].blue = fg_color[2];
		palette[1].red = bg_color[0];
		palette[1].green = bg_color[1];
		palette[1].blue = bg_color[2];
		alpha_values[0] = fg_color[3];
		alpha_values[1] = bg_color[3];
		png_set_PLTE(png_ptr, info_ptr, palette, 2);
		png_set_tRNS(png_ptr, info_ptr, alpha_values, 2, NULL);
	}

	png_init_io(png_ptr, fp);
	if (type == PNG_TYPE) {
		png_set_IHDR(png_ptr, info_ptr,
			realwidth, realwidth,
			1,
			PNG_COLOR_TYPE_PALETTE,
			PNG_INTERLACE_NONE,
			PNG_COMPRESSION_TYPE_DEFAULT,
			PNG_FILTER_TYPE_DEFAULT);
	}
	else {
		png_set_IHDR(png_ptr, info_ptr,
			realwidth, realwidth,
			8,
			PNG_COLOR_TYPE_RGB_ALPHA,
			PNG_INTERLACE_NONE,
			PNG_COMPRESSION_TYPE_DEFAULT,
			PNG_FILTER_TYPE_DEFAULT);
	}
	png_set_pHYs(png_ptr, info_ptr,
		dpi * INCHES_PER_METER,
		dpi * INCHES_PER_METER,
		PNG_RESOLUTION_METER);
	png_write_info(png_ptr, info_ptr);

	if (type == PNG_TYPE) {
		/* top margin */
		memset(row, 0xff, (realwidth + 7) / 8);
		for (y = 0; y < margin * size; y++) {
			png_write_row(png_ptr, row);
		}

		/* data */
		p = qrcode->data;
		for (y = 0; y < qrcode->width; y++) {
			memset(row, 0xff, (realwidth + 7) / 8);
			q = row;
			q += margin * size / 8;
			bit = 7 - (margin * size % 8);
			for (x = 0; x < qrcode->width; x++) {
				for (xx = 0; xx < size; xx++) {
					*q ^= (*p & 1) << bit;
					bit--;
					if (bit < 0) {
						q++;
						bit = 7;
					}
				}
				p++;
			}
			for (yy = 0; yy < size; yy++) {
				png_write_row(png_ptr, row);
			}
		}
		/* bottom margin */
		memset(row, 0xff, (realwidth + 7) / 8);
		for (y = 0; y < margin * size; y++) {
			png_write_row(png_ptr, row);
		}
	}
	else {
		/* top margin */
		fillRow(row, realwidth, bg_color);
		for (y = 0; y < margin * size; y++) {
			png_write_row(png_ptr, row);
		}

		/* data */
		p = qrcode->data;
		for (y = 0; y < qrcode->width; y++) {
			fillRow(row, realwidth, bg_color);
			for (x = 0; x < qrcode->width; x++) {
				for (xx = 0; xx < size; xx++) {
					if (*p & 1) {
						memcpy(&row[((margin + x) * size + xx) * 4], fg_color, 4);
					}
				}
				p++;
			}
			for (yy = 0; yy < size; yy++) {
				png_write_row(png_ptr, row);
			}
		}
		/* bottom margin */
		fillRow(row, realwidth, bg_color);
		for (y = 0; y < margin * size; y++) {
			png_write_row(png_ptr, row);
		}
	}

	png_write_end(png_ptr, info_ptr);
	png_destroy_write_struct(&png_ptr, &info_ptr);

	fclose(fp);
	free(row);
	free(palette);

	return 0;
}

static QRcode *encode(const char *intext)
{
	QRcode *code;

	code = QRcode_encodeString(intext, version, level, hint, casesensitive);

	return code;
}


static int qrencode(const char *intext, const char *outfile, enum imageType image_type)
{
	int result = 0;
	QRcode *qrcode = encode(intext);

	if (qrcode == NULL) {
		if (errno == ERANGE) {
			fprintf(stderr, "Failed to encode the input data: Input data too large\n");
		}
		else {
			perror("Failed to encode the input data");
		}
		return 1;
	}

	if (verbose) {
		fprintf(stderr, "File: %s, Version: %d\n", (outfile != NULL) ? outfile : "(stdout)", qrcode->version);
	}

	switch (image_type) {
	case PNG_TYPE:
	case PNG32_TYPE:
		result = writePNG(qrcode, outfile, image_type);
		break;
	default:
		fprintf(stderr, "Unknown image type.\n");
		return 1;
	}

	QRcode_free(qrcode);

	return result;
}

int genqr(const char * intext, const char * outfile)
{
	return qrencode(intext, outfile, PNG_TYPE);
}
