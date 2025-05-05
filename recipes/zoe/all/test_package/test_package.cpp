#include <iostream>
#include "zoe/zoe.h"

int main(int argc, char** argv) {
  using namespace zoe;

  Zoe::GlobalInit();

  Zoe efd;

  efd.setThreadNum(10);                     // Optional
  efd.setTmpFileExpiredTime(3600);          // Optional
  efd.setDiskCacheSize(20 * (2 << 19));     // Optional
  efd.setMaxDownloadSpeed(50 * (2 << 19));  // Optional
  efd.setHashVerifyPolicy(ALWAYS, MD5, "6fe294c3ef4765468af4950d44c65525"); // Optional, support MD5, CRC32, SHA256
  // There are more options available, please check zoe.h
  efd.setVerboseOutput([](const utf8string& verbose) { // Optional
    printf("%s\n", verbose.c_str());
  });
  efd.setHttpHeaders({  // Optional
    {"Origin", "http://xxx.xxx.com"},
    {"User-Agent", "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"}
   });

  Zoe::GlobalUnInit();

  return 0;
}
