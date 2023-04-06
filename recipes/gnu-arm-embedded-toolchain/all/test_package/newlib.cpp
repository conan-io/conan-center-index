#include <sys/stat.h>
#include <unistd.h>

#include <cstdarg>
#include <cstdint>
#include <cstdio>
#include <cstring>

extern "C"
{
  /// Dummy implementation of getpid
  int _getpid_r()
  {
    return 1;
  }

  /// Dummy implementation of kill
  int _kill_r(int, int)
  {
    return -1;
  }

  /// Dummy implementation of fstat, makes the assumption that the "device"
  /// representing, in this case STDIN, STDOUT, and STDERR as character devices.
  int _fstat_r([[maybe_unused]] int file, struct stat* status)
  {
    status->st_mode = S_IFCHR;
    return 0;
  }

  int _write_r([[maybe_unused]] int file,
               [[maybe_unused]] const char* ptr,
               int length)
  {
    return length;
  }

  int _read_r([[maybe_unused]] FILE* file,
              [[maybe_unused]] char* ptr,
              int length)
  {
    return length;
  }

  // Dummy implementation of _lseek
  int _lseek_r([[maybe_unused]] int file,
               [[maybe_unused]] int ptr,
               [[maybe_unused]] int dir)
  {
    return 0;
  }

  // Dummy implementation of close
  int _close_r([[maybe_unused]] int file)
  {
    return -1;
  }

  // Dummy implementation of isatty
  int _isatty_r([[maybe_unused]] int file)
  {
    return 1;
  }
}
