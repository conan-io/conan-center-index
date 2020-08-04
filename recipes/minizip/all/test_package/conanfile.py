from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    _cmake = None

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["CONAN_MZ_VERSION"] = self.requires["minizip"].ref.version
            if self.options["minizip"].compress_only:
                self._cmake.definitions["MZ_ZIP_NO_DECOMPRESSION"] = "MZ_ZIP_NO_DECOMPRESSION"
            if self.options["minizip"].decompress_only:
                self._cmake.definitions["MZ_ZIP_NO_COMPRESSION"] = "MZ_ZIP_NO_COMPRESSION"
            if self.options["minizip"].bzip2:
                self._cmake.definitions["HAVE_BZIP2"] = "HAVE_BZIP2"
            if self.options["minizip"].zlib:
                self._cmake.definitions["HAVE_ZLIB"] = "HAVE_ZLIB"
            if self.options["minizip"].lzma:
                self._cmake.definitions["HAVE_LZMA"] = "HAVE_LZMA"
            if self.options["minizip"].zstd:
                self._cmake.definitions["HAVE_ZSTD"] = "HAVE_ZSTD"
            if self.options["minizip"].compat:
                self._cmake.definitions["HAVE_COMPAT"] = "HAVE_COMPAT"
            if self.options["minizip"].pkcrypt:
                self._cmake.definitions["HAVE_PKCRYPT"] = "HAVE_PKCRYPT"
            if self.options["minizip"].wzaes:
                self._cmake.definitions["HAVE_WZAES"] = "HAVE_WZAES"
            if not self.options["minizip"].wzaes and not self.options["minizip"].pkcrypt:
                self._cmake.definitions["MZ_ZIP_NO_ENCRYPTION"] = "MZ_ZIP_NO_ENCRYPTION"
            self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
