#pragma once

#include <filesystem>

namespace fs = std::filesystem;

namespace conan::recipe {

  class ScopedTempDir {
    public:
      ScopedTempDir();

      ~ScopedTempDir() {
        fs::remove_all(path);
      }

      const fs::path &GetPath() {
        return path;
      }

    private:

      // (move constructor and move assignment implicitly deleted due to
      // declared destructor); make non-copyable as well
      ScopedTempDir(const ScopedTempDir&) = delete;
      ScopedTempDir& operator=(const ScopedTempDir&) = delete;

      fs::path path;
  };

}
