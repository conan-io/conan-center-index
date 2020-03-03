#include <SZconfig.h>
#include <szlib.h>

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

unsigned long szip_decoding(int bits_per_pixel, char *in, long size, char *out, long out_size, long buffer_size) {
  int bytes_per_pixel;
  int err;
  sz_stream d_stream;

  strcpy((char*)out, "garbage");

  d_stream.hidden = 0;

  d_stream.next_in  = in;
  d_stream.next_out = out;

  d_stream.avail_in = 0;
  d_stream.avail_out = 0;

  d_stream.total_in = 0;
  d_stream.total_out = 0;

  d_stream.options_mask = SZ_RAW_OPTION_MASK | SZ_NN_OPTION_MASK | SZ_MSB_OPTION_MASK;
  d_stream.bits_per_pixel = bits_per_pixel;
  d_stream.pixels_per_block = 8;
  d_stream.pixels_per_scanline = 16;

  bytes_per_pixel = (bits_per_pixel + 7)/8;
  if (bytes_per_pixel == 3) bytes_per_pixel = 4;

  d_stream.image_pixels = out_size/bytes_per_pixel;

  err = SZ_DecompressInit(&d_stream);
  if (err != SZ_OK) {
    fprintf(stderr, "SZ_DecompressEnd error: %d\n", err);
    exit(0);
  }

  while (d_stream.total_in < size) {
    d_stream.avail_in = d_stream.avail_out = buffer_size;
    if (d_stream.avail_in + d_stream.total_in > size)
      d_stream.avail_in = size - d_stream.total_in;

    err = SZ_Decompress(&d_stream, SZ_NO_FLUSH);
    if (err == SZ_STREAM_END) break;

    if (err != SZ_OK) {
      fprintf(stderr, "SZ_Decompress error: %d\n", err);
      exit(0);
    }
  }

  while (d_stream.total_out < out_size) {
    d_stream.avail_out = buffer_size;
    err = SZ_Decompress(&d_stream, SZ_FINISH);
    if (err == SZ_STREAM_END) break;

    if (err != SZ_OK) {
      fprintf(stderr, "SZ_Decompress error: %d\n", err);
      exit(0);
    }
  }

  err = SZ_DecompressEnd(&d_stream);
  if (err != SZ_OK) {
    fprintf(stderr, "SZ_DecompressEnd error: %d\n", err);
    exit(0);
  }

  return d_stream.total_out;
}

int main() {
  char *out = (char *) malloc(1024*1024L);
  unsigned long size = szip_decoding(8, NULL, 0, out, 0, 1);
  return 0;
}
