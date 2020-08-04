#include <stdio.h>

#include <mz.h>
#ifdef HAVE_COMPAT
#include <mz_compat.h>
#endif
#ifndef MZ_ZIP_NO_ENCRYPTION
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

int test_mz() { return strcmp(MZ_VERSION, CONAN_MZ_VERSION); }

#ifdef HAVE_COMPAT
int test_mz_compat() {
  printf("Test mz_compat:\n");
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

#ifndef MZ_ZIP_NO_ENCRYPTION
int test_mz_crypt() {
  printf("Test mz_crypt:\n");
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

int test_mz_strm_create(char const *methodName,
                        mz_stream_create_cb streamFractory) {
  printf("Test mz_strm: mz_stream_%s_create\n", methodName);

  void *stream = NULL;
  if (streamFractory(&stream) == NULL) {
    printf("Failed to create stream %s.", methodName);
    return 1;
  }
  mz_stream_delete(&stream);

  return 0;
}

int test_mz_os() {
  printf("Test mz_os:\n");
  {
    printf("Test mz_os: mz_path\n");

    char path[128] = "foo";
    if (mz_path_combine(path, "bar", 128) != 0) {
      printf("Failed to combine paths.\n");
      return 1;
    }
  }
  {
    printf("Test mz_os: mz_os_unicode\n");

    wchar_t *str =
        mz_os_unicode_string_create(u8"\u0100", MZ_ENCODING_CODEPAGE_437);
    if (str == NULL) {
      printf("Failed to create unicode string.");
      return 1;
    }
    mz_os_unicode_string_delete(&str);
  }
  return 0;
}

int test_mz_strm() {
  printf("Test mz_strm:\n");
  int err = 0;

  // Unconditionaly available stream types
  err |= test_mz_strm_create("os", mz_stream_os_create);
  err |= test_mz_strm_create("mem", mz_stream_mem_create);
  err |= test_mz_strm_create("buffered", mz_stream_buffered_create);
  err |= test_mz_strm_create("split", mz_stream_split_create);

// Conditionaly available stream types
#ifdef HAVE_LIBCOMP
  err |= test_mz_strm_create("libcomp", mz_stream_libcomp_create);
#endif
#ifdef HAVE_ZLIB
  err |= test_mz_strm_create("zlib", mz_stream_zlib_create);
#endif
#ifdef HAVE_BZIP
  err |= test_mz_strm_create("bzip", mz_stream_bzip_create);
#endif
#ifdef HAVE_PKGCRYPT
  err |= test_mz_strm_create("pkcrypt", mz_stream_pkcrypt_create);
#endif
#ifdef HAVE_LZMA
  err |= test_mz_strm_create("lzma", mz_stream_lzma_create);
#endif
#ifdef HAVE_WZAES
  err |= test_mz_strm_create("wzaes", mz_stream_wzaes_create);
#endif
#ifdef HAVE_ZSTD
  err |= test_mz_strm_create("zstd", mz_stream_zstd_create);
#endif

  return err;
}

int main(int argc, const char *argv[]) {
  int err = 0;

  err |= test_mz();
#ifdef HAVE_COMPAT
  err |= test_mz_compat();
#endif
#ifndef MZ_ZIP_NO_ENCRYPTION
  err |= test_mz_crypt();
#endif
  err |= test_mz_os();
  err |= test_mz_strm();

  return err;
}
