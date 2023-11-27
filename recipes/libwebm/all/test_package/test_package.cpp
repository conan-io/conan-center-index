#include <cstdint>
#include <cstdio>

#ifdef UNPREFIXED_HEADERS
#include <webm/mkvmuxerutil.h>
#include <webm/mkvparser.h>
#else
#include <webm/mkvmuxer/mkvmuxerutil.h>
#include <webm/mkvparser/mkvparser.h>
#endif // UNPREFIXED_HEADERS

int main(void) {
  int32_t major, minor, build, revision;

  mkvparser::GetVersion(major, minor, build, revision);
  printf("Mkv Parser version: %d.%d.%d.%d\n", major, minor, build, revision);

  mkvmuxer::GetVersion(&major, &minor, &build, &revision);
  printf("Mkv Muxer version: %d.%d.%d.%d\n", major, minor, build, revision);

  return 0;
}
