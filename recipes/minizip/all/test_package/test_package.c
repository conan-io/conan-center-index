#include <stdio.h>

#define MAX_STREAM_NAME_SIZE 256
#define MAX_STREAM_PATH_SIZE 256
#define MAX_STREAM_PROPERTIES 8

#include <mz.h>
#ifdef HAVE_COMPAT
#include <mz_compat.h>
#endif
#ifdef HAVE_ENCRYPTION
#include <mz_crypt.h>
#endif
#include <mz_os.h>
#include <mz_strm.h>
#include <mz_strm_buf.h>
#include <mz_strm_mem.h>
#include <mz_strm_os.h>
#include <mz_strm_split.h>
#ifdef HAVE_BZIP
#include <mz_strm_bzip.h>
#endif
#ifdef HAVE_LZMA
#include <mz_strm_lzma.h>
#endif
#ifdef HAVE_PKCRYPT
#include <mz_strm_pkcrypt.h>
#endif
#ifdef HAVE_WZAES
#include <mz_strm_wzaes.h>
#endif
#ifdef HAVE_ZLIB
#include <mz_strm_zlib.h>
#endif
#ifdef HAVE_ZSTD
#include <mz_strm_zstd.h>
#endif
#ifdef HAVE_LIBCOMP
#include <mz_strm_libcomp.h>
#endif
#include <mz_zip.h>

int test_mz() {
  printf("Test MZ_VERSION:\n");
  return strcmp(MZ_VERSION, CONAN_MZ_VERSION);
}

#ifdef HAVE_COMPAT
int test_mz_compat() {
  {
    printf("Test mz_compat: zip\n");

    zipFile zf = zipOpen64("foo.zip", APPEND_STATUS_CREATE);
    if (zf == NULL) {
      printf("Failed to open file.\n");
      return 1;
    }
    if (zipClose_64(zf, NULL) != 0) {
      printf("Failed to close file.\n");
      return 1;
    }
  }
  {
    printf("Test mz_compat: unzip\n");

    unzFile zf = unzOpen64("foo.zip");
    if (zf == NULL) {
      printf("Failed to open zipfile.\n");
      return 1;
    }
    if (unzClose(zf) != 0) {
      printf("Failed to close zipfile.\n");
      return 1;
    }
  }
  return 0;
}
#endif

#ifdef HAVE_ENCRYPTION
int test_mz_crypt() {
  {
    printf("Test mz_crypt: mz_crypt_crc32\n");

    const char testData[] = "Lorem Ipsum";
    const uint32_t testDataCrc32 = 0x358AD45D;

    uint32_t crc32 = 0;
    crc32 = mz_crypt_crc32_update(crc32, (uint8_t *)testData,
                                  (uint32_t)strlen(testData));
    if (testDataCrc32 != crc32) {
      printf("Failed to verify crc32.\n");
      return 1;
    }
  }
  {
    printf("Test mz_crypt: mz_crypt_aes\n");

    void *aes = NULL;
    if (mz_crypt_aes_create(&aes) == NULL) {
      printf("Failed to create aes handle.");
      return 1;
    }
    mz_crypt_aes_delete(&aes);
  }
  {
    printf("Test mz_crypt: mz_crypt_hmac\n");

    void *hmac = NULL;
    if (mz_crypt_hmac_create(&hmac) == NULL) {
      printf("Failed to create hmac handle.");
      return 1;
    }
    mz_crypt_hmac_delete(&hmac);
  }
  {
    printf("Test mz_crypt: mz_crypt_sha\n");

    void *sha = NULL;
    if (mz_crypt_sha_create(&sha) == NULL) {
      printf("Failed to create sha handle.");
      return 1;
    }
    mz_crypt_sha_delete(&sha);
  }
  return 0;
}
#endif

int test_mz_os() {
  {
    printf("Test mz_os: mz_path\n");

    char path[128] = "foo";
    if (mz_path_combine(path, "bar", 128) != 0) {
      printf("Failed to combine paths.\n");
      return 1;
    }
  }
  return 0;
}

struct StreamProperty {
  int32_t prop;
  int64_t value;
};

struct PipelineElement {
  mz_stream_create_cb streamFactory;
  char name[MAX_STREAM_NAME_SIZE];
  void *stream;
  char path[MAX_STREAM_PATH_SIZE];
  int mode;
  struct StreamProperty proprties[MAX_STREAM_PROPERTIES];
};

struct PipelineElement createPipelineElement(mz_stream_create_cb streamFactory,
                                             char const *name,
                                             char const *path) {
  struct PipelineElement element;
  element.streamFactory = streamFactory;
  if (name != NULL)
    strncpy_s(&element.name[0], MAX_STREAM_NAME_SIZE, name,
              strnlen_s(name, MAX_STREAM_NAME_SIZE));
  else
    memset(&element.name[0], 0, MAX_STREAM_NAME_SIZE);
  element.stream = NULL;
  if (path != NULL)
    strncpy_s(&element.path[0], MAX_STREAM_PATH_SIZE, path,
              strnlen_s(path, MAX_STREAM_PATH_SIZE));
  else
    memset(&element.path[0], 0, MAX_STREAM_PATH_SIZE);
  element.mode = 0;
  for (size_t i = 0; i < MAX_STREAM_PROPERTIES; ++i) {
    element.proprties[i].prop = -1;
    element.proprties[i].value = -1;
  }
  return element;
}

struct PipelineElement
createPipelineElement_name(mz_stream_create_cb streamFactory,
                           char const *name) {
  return createPipelineElement(streamFactory, name, NULL);
}

struct PipelineElement
createPipelineElement_bare(mz_stream_create_cb streamFactory) {
  return createPipelineElement(streamFactory, NULL, NULL);
}

int strm_create_streams(struct PipelineElement *elements[],
                        int const elementCount) {
  int err = 0;
  for (int i = 0; i < elementCount; ++i) {
    struct PipelineElement *current = elements[i];
    if (current->streamFactory(&current->stream) == NULL) {
      printf("Failed to create stream %s.\n", current->name);
      err |= 1;
    }
  }
  return err;
}

int strm_set_stream_bases(struct PipelineElement *elements[],
                          int const elementCount) {
  int err = 0;
  for (int i = 0; i < elementCount; ++i) {
    struct PipelineElement *current = elements[i];
    struct PipelineElement *next =
        i + 1 < elementCount ? elements[i + 1] : NULL;
    if (next != NULL) {
      if (mz_stream_set_base(current->stream, next->stream) != 0) {
        printf("Failed to set stream base %s.\n", current->name);
        err |= 1;
      }
    }
  }
  return err;
}

int strm_open_streams(struct PipelineElement *elements[],
                      int const elementCount) {
  int err = 0;
  for (int i = elementCount - 1; i >= 0; --i) {
    struct PipelineElement *current = elements[i];
    if (mz_stream_is_open(current->stream) == 0)
      continue;
    if (mz_stream_open(current->stream, current->path, current->mode) != 0) {
      printf("Failed to open stream %s.\n", current->name);
      err |= 1;
    }
  }
  return err;
}

int strm_close_streams(struct PipelineElement *elements[],
                       int const elementCount) {
  int err = 0;
  for (int i = 0; i < elementCount; ++i) {
    struct PipelineElement *current = elements[i];
    if (mz_stream_is_open(current->stream) != 0)
      continue;
    if (mz_stream_close(current->stream) != 0) {
      printf("Failed to close stream %s.\n", current->name);
      err |= 1;
    }
  }
  return err;
}

int strm_delete_streams(struct PipelineElement *elements[],
                        int const elementCount) {
  for (int i = 0; i < elementCount; ++i) {
    struct PipelineElement *current = elements[i];
    mz_stream_delete(&current->stream);
  }
  return 0;
}

int strm_set_modes(struct PipelineElement *elements[], int const elementCount,
                   int const modes) {
  for (int i = 0; i < elementCount; ++i) {
    elements[i]->mode = modes;
  }
  return 0;
}

int strm_set_properties(struct PipelineElement *elements[],
                        int const elementCount) {
  int err = 0;
  for (int i = 0; i < elementCount; ++i) {
    struct PipelineElement *current = elements[i];
    for (size_t j = 0; j < MAX_STREAM_PROPERTIES; ++j) {
      if (current->proprties[j].prop >= 0 &&
          mz_stream_set_prop_int64(current->stream, current->proprties[j].prop,
                                   current->proprties[j].value) != 0) {
        printf("Failed to set property for stream %s.\n", current->name);
        err |= 1;
      }
    }
  }
  return err;
}

int strm_write_data(struct PipelineElement *pipe, const size_t bytesToWrite,
                    int32_t *crc) {
  int err = 0;
  srand(0);

  uint8_t buffer[1024];
  size_t newBytes = 0;

  for (size_t i = 0; i < bytesToWrite && err == 0; i += newBytes) {
    newBytes = bytesToWrite < sizeof(buffer) ? bytesToWrite : sizeof(buffer);

    for (size_t j = 0; j < newBytes; ++j) {
      buffer[j] = rand();
    }

    *crc = mz_crypt_crc32_update(*crc, &buffer[0], (int32_t)newBytes);
    if (mz_stream_write(pipe->stream, &buffer[0], (int32_t)newBytes) !=
        (int32_t)newBytes) {
      printf("Failed to write into stream %s.\n", pipe->name);
      err |= 1;
    }
  }

  return err;
}

int strm_read_data(struct PipelineElement *pipe, int32_t const bytesToRead,
                   int32_t expectedCrc) {
  int32_t actualCrc = 0;
  char buff[1024];
  int readBytes = 0;
  int totalBytesRead = 0;
  int maxBytesToRead = sizeof(buff);

  while ((readBytes = mz_stream_read(pipe->stream, buff, maxBytesToRead)) > 0 &&
         totalBytesRead < bytesToRead) {
    totalBytesRead += readBytes;

    actualCrc = mz_crypt_crc32_update(actualCrc, (uint8_t *)buff, readBytes);

    if (maxBytesToRead > bytesToRead - totalBytesRead)
      maxBytesToRead = bytesToRead - totalBytesRead;
  }

  if (actualCrc != expectedCrc) {
    printf("Failed to verify crc.\n");
    return 1;
  } else {
    return 0;
  }
}

int strm_print_pipeline(struct PipelineElement *elements[],
                        int const elementCount) {
  printf("Test mz_strm: ");
  for (int i = 0; i < elementCount; ++i) {
    printf("%s", elements[i]->name);
    if (i + 1 < elementCount) {
      printf(" <-> ");
    }
  }
  printf("\n");
  return 0;
}

int strm_test(struct PipelineElement *elements[], int const elementCount) {
  int err = 0;
  int32_t expectedCrc = 0;
  int bytes_to_write = 1024;

  err |= strm_print_pipeline(elements, elementCount);

  err |= strm_set_modes(elements, elementCount,
                        MZ_OPEN_MODE_WRITE | MZ_OPEN_MODE_CREATE);
  err |= strm_create_streams(elements, elementCount);
  err |= strm_set_properties(elements, elementCount);
  err |= strm_set_stream_bases(elements, elementCount);
  err |= strm_open_streams(elements, elementCount);
  err |= strm_write_data(elements[0], bytes_to_write, &expectedCrc);
  err |= strm_close_streams(elements, elementCount);
  err |= strm_delete_streams(elements, elementCount);

  err |= strm_set_modes(elements, elementCount, MZ_OPEN_MODE_READ);
  err |= strm_create_streams(elements, elementCount);
  err |= strm_set_properties(elements, elementCount);
  err |= strm_set_stream_bases(elements, elementCount);
  err |= strm_open_streams(elements, elementCount);
  err |= strm_read_data(elements[0], bytes_to_write, expectedCrc);
  err |= strm_close_streams(elements, elementCount);
  err |= strm_delete_streams(elements, elementCount);

  return err;
}

int test_mz_strm() {

  int err = 0;

  {
    struct PipelineElement os_pipe =
        createPipelineElement(mz_stream_os_create, "os", "data.buffered");
    struct PipelineElement buffered_pipe =
        createPipelineElement_name(mz_stream_buffered_create, "buffered");
    struct PipelineElement *pipe[] = {&buffered_pipe, &os_pipe};
    err |= strm_test(pipe, sizeof(pipe) / sizeof(struct PipelineElement *));
  }
#if defined(HAVE_ZLIB) && defined(HAVE_COMPRESS) && defined(HAVE_DECOMPRESS)
  {
    struct PipelineElement os_pipe =
        createPipelineElement(mz_stream_os_create, "os", "data.zlib");
    struct PipelineElement zlib_pipe =
        createPipelineElement_name(mz_stream_zlib_create, "zlib");
    struct PipelineElement *pipe[] = {&zlib_pipe, &os_pipe};
    err |= strm_test(pipe, sizeof(pipe) / sizeof(struct PipelineElement *));
  }
#endif
#if defined(HAVE_LZMA) && defined(HAVE_COMPRESS) && defined(HAVE_DECOMPRESS)
  {
    struct PipelineElement os_pipe =
        createPipelineElement(mz_stream_os_create, "os", "data.lzma");
    struct PipelineElement lzma_pipe =
        createPipelineElement_name(mz_stream_lzma_create, "lzma");
    struct PipelineElement *pipe[] = {&lzma_pipe, &os_pipe};
    err |= strm_test(pipe, sizeof(pipe) / sizeof(struct PipelineElement *));
  }
#endif
#if defined(HAVE_BZIP) && defined(HAVE_COMPRESS) && defined(HAVE_DECOMPRESS)
  {
    struct PipelineElement os_pipe =
        createPipelineElement(mz_stream_os_create, "os", "data.bzip");
    struct PipelineElement bzip_pipe =
        createPipelineElement_name(mz_stream_bzip_create, "bzip");
    struct PipelineElement *pipe[] = {&bzip_pipe, &os_pipe};
    err |= strm_test(pipe, sizeof(pipe) / sizeof(struct PipelineElement *));
  }
#endif
#if defined(HAVE_ZSTD) && defined(HAVE_COMPRESS) && defined(HAVE_DECOMPRESS)
  {
    struct PipelineElement os_pipe =
        createPipelineElement(mz_stream_os_create, "os", "data.zstd");
    struct PipelineElement zstd_pipe =
        createPipelineElement_name(mz_stream_zstd_create, "zstd");
    struct PipelineElement *pipe[] = {&zstd_pipe, &os_pipe};
    err |= strm_test(pipe, sizeof(pipe) / sizeof(struct PipelineElement *));
  }
#endif
#if defined(HAVE_WZAES) && defined(HAVE_COMPRESS) && defined(HAVE_DECOMPRESS)
  {
    struct PipelineElement os_pipe =
        createPipelineElement(mz_stream_os_create, "os", "data.wzaes");
    struct PipelineElement wzaes_pipe =
        createPipelineElement(mz_stream_wzaes_create, "wzaes", "password");

    wzaes_pipe.proprties[0].prop = MZ_STREAM_PROP_TOTAL_IN_MAX;
    wzaes_pipe.proprties[0].value = 1024 * 1024 * 10;

    struct PipelineElement *pipe[] = {&wzaes_pipe, &os_pipe};
    err |= strm_test(pipe, sizeof(pipe) / sizeof(struct PipelineElement *));
  }
#endif
#if defined(HAVE_PKCRYPT) && defined(HAVE_COMPRESS) && defined(HAVE_DECOMPRESS)
  {
    struct PipelineElement os_pipe =
        createPipelineElement(mz_stream_os_create, "os", "data.wzaes");
    struct PipelineElement pkcrypt_pipe =
        createPipelineElement(mz_stream_pkcrypt_create, "pkcrypt", "password");

    pkcrypt_pipe.proprties[0].prop = MZ_STREAM_PROP_TOTAL_IN_MAX;
    pkcrypt_pipe.proprties[0].value = 1024 * 1024 * 10;

    struct PipelineElement *pipe[] = {&pkcrypt_pipe, &os_pipe};
    err |= strm_test(pipe, sizeof(pipe) / sizeof(struct PipelineElement *));
  }
#endif
#if defined(HAVE_LIBCOMP) && defined(HAVE_COMPRESS) && defined(HAVE_DECOMPRESS)
  {
    struct PipelineElement os_pipe =
        createPipelineElement(mz_stream_os_create, "os", "data.libcomp");
    struct PipelineElement libcomp_pipe =
        createPipelineElement_name(mz_stream_libcomp_create, "libcomp");

    struct PipelineElement *pipe[] = {&libcomp_pipe, &os_pipe};
    err |= strm_test(pipe, sizeof(pipe) / sizeof(struct PipelineElement *));
  }
#endif

  return err;
}

int test_mz_zip() {
  printf("Test mz_zip:");

  int err = 0;
  void *zipHandle = NULL;
  char filename_in_zip[] = "Hello.txt";
  char data[] =
      "Hello, World!\nHello, World!\nHello, World!\nHello, World!\nHello, "
      "World!\nHello, World!\nHello, World!\nHello, World!\nHello, World!\n";
  int32_t bytes_written = 0;

  struct PipelineElement os_pipe =
      createPipelineElement(mz_stream_os_create, "os", "mz_zip.zip");
  struct PipelineElement *pipe[] = {&os_pipe};
  int const pipe_size = sizeof(pipe) / sizeof(struct PipelineElement *);

  mz_zip_file file_info;
  memset(&file_info, 0, sizeof(mz_zip_file));
  file_info.compression_method = MZ_COMPRESS_METHOD_STORE;
  file_info.filename = &filename_in_zip[0];
  file_info.version_madeby = MZ_VERSION_MADEBY;
  file_info.uncompressed_size = strlen(data);

  mz_zip_create(&zipHandle);

  err |= strm_create_streams(pipe, pipe_size);
  err |= strm_set_modes(pipe, pipe_size, MZ_OPEN_MODE_CREATE);
  err |= strm_open_streams(pipe, pipe_size);
  err |= mz_zip_open(zipHandle, pipe[0]->stream, MZ_OPEN_MODE_WRITE);
  err |= mz_zip_entry_write_open(zipHandle, &file_info,
                                 MZ_COMPRESS_LEVEL_DEFAULT, 0, NULL);

  bytes_written = mz_zip_entry_write(zipHandle, data, (int32_t)strlen(data));
  if (bytes_written < MZ_OK)
    err |= 1;

  err |= mz_zip_entry_close(zipHandle);
  err |= mz_zip_close(zipHandle);
  err |= strm_close_streams(pipe, pipe_size);
  err |= strm_delete_streams(pipe, pipe_size);

  mz_zip_delete(&zipHandle);

  return err;
}

int main(int argc, const char *argv[]) {
  int err = 0;

  err |= test_mz();
#ifdef HAVE_COMPAT
  err |= test_mz_compat();
#endif
#ifdef HAVE_ENCRYPTION
  err |= test_mz_crypt();
#endif
  err |= test_mz_os();
  err |= test_mz_strm();
  err |= test_mz_zip();

  return err;
}
