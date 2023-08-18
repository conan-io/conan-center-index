#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "fpzip.h"

static size_t
compress(FPZ* fpz, const void* data)
{
  size_t size;
  /* write header */
  if (!fpzip_write_header(fpz)) {
    fprintf(stderr, "cannot write header: %s\n", fpzip_errstr[fpzip_errno]);
    return 0;
  }
  /* perform actual compression */
  size = fpzip_write(fpz, data);
  if (!size) {
    fprintf(stderr, "compression failed: %s\n", fpzip_errstr[fpzip_errno]);
    return 0;
  }
  return size;
}

static int
decompress(FPZ* fpz, void* data, size_t inbytes)
{
  /* read header */
  if (!fpzip_read_header(fpz)) {
    fprintf(stderr, "cannot read header: %s\n", fpzip_errstr[fpzip_errno]);
    return 0;
  }
  /* make sure array size stored in header matches expectations */
  if ((fpz->type == FPZIP_TYPE_FLOAT ? sizeof(float) : sizeof(double)) * fpz->nx * fpz->ny * fpz->nz * fpz->nf != inbytes) {
    fprintf(stderr, "array size does not match dimensions from header\n");
    return 0;
  }
  /* perform actual decompression */
  if (!fpzip_read(fpz, data)) {
    fprintf(stderr, "decompression failed: %s\n", fpzip_errstr[fpzip_errno]);
    return 0;
  }
  return 1;
}

static float
float_rand()
{
  static unsigned int seed = 1;
  double val;
  seed = 1103515245 * seed + 12345;
  seed &= 0x7fffffffu;
  val = ldexp((double)seed, -31);
  val = 2 * val - 1;
  val *= val * val;
  val *= val * val;
  return val;
}

/* generate a trilinear field perturbed by random noise */
float*
float_field(int nx, int ny, int nz, float offset)
{
  int n = nx * ny * nz;
  float* field = malloc(n * sizeof(float));
  int i, x, y, z;
  /* generate random field */
  *field = offset;
  for (i = 1; i < n; i++)
    field[i] = float_rand();
  /* integrate along x */
  for (z = 0; z < nz; z++)
    for (y = 0; y < ny; y++)
      for (x = 1; x < nx; x++)
        field[x + nx * (y + ny * z)] += field[(x - 1) + nx * (y + ny * z)];
  /* integrate along y */
  for (z = 0; z < nz; z++)
    for (y = 1; y < ny; y++)
      for (x = 0; x < nx; x++)
        field[x + nx * (y + ny * z)] += field[x + nx * ((y - 1) + ny * z)];
  /* integrate along z */
  for (z = 1; z < nz; z++)
    for (y = 0; y < ny; y++)
      for (x = 0; x < nx; x++)
        field[x + nx * (y + ny * z)] += field[x + nx * (y + ny * (z - 1))];
  return field;
}

static void
test_float_array(const float* field, int nx, int ny, int nz, int prec)
{
  int status;
  unsigned int actual_checksum;
  int dims = (nz == 1 ? ny == 1 ? 1 : 2 : 3);
  size_t inbytes = nx * ny * nz * sizeof(float);
  size_t bufbytes = 1024 + inbytes;
  size_t outbytes = 0;
  void* buffer = malloc(bufbytes);
  float* copy = malloc(inbytes);
  char name[0x100];

  /* compress to memory */
  FPZ* fpz = fpzip_write_to_buffer(buffer, bufbytes);
  fpz->type = FPZIP_TYPE_FLOAT;
  fpz->prec = prec;
  fpz->nx = nx;
  fpz->ny = ny;
  fpz->nz = nz;
  fpz->nf = 1;
  outbytes = compress(fpz, field);
  status = (0 < outbytes && outbytes <= bufbytes);
  fpzip_write_close(fpz);
  sprintf(name, "test.float.%dd.prec%d.compress", dims, prec);

  /* decompress */
  fpz = fpzip_read_from_buffer(buffer);
  status = decompress(fpz, copy, inbytes);
  fpzip_read_close(fpz);
  sprintf(name, "test.float.%dd.prec%d.decompress", dims, prec);

  free(copy);
  free(buffer);
}

static int
test_float(int nx, int ny, int nz)
{
  float* field = float_field(nx, ny, nz, 0);
  int prec = 8;
  test_float_array(field, nx * ny * nz, 1, 1, prec);
  test_float_array(field, nx, ny * nz, 1, prec);
  test_float_array(field, nx, ny, nz, prec);
  free(field);
}

int main(void) {
  test_float(65, 64, 63);

  return 0;
}
