from conans import ConanFile, tools, CMake
import os
import glob

required_conan_version = ">=1.33.0"

class LibgcryptConan(ConanFile):
    name = "libgcrypt"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnupg.org/download/index.html#libgcrypt"
    description = "Libgcrypt is a general purpose cryptographic library originally based on code from GnuPG"
    topics = ("conan", "libgcrypt", "gcrypt", "gnupg", "gpg", "crypto", "cryptography")
    license = "LGPL-2.1-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt", "patches/**", "config.h.in", "gcrypt.h.in", "mod-source-info.h"]
    generators = "cmake"

    requires = 'libgpg-error/1.36'

    exports_sources = "CMakeLists.txt", "config.h.in", "gcrypt.h.in", "mod-source-info.h", "patches/**"

    _cmake = None

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        if self._is_msvc:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)
            os.makedirs(os.path.join(self._source_subfolder, "sys"))
            tools.download("https://raw.githubusercontent.com/win32ports/unistd_h/master/unistd.h",
                           os.path.join(self._source_subfolder, "unistd.h"))
            tools.download("https://raw.githubusercontent.com/win32ports/sys_time_h/master/sys/time.h",
                           os.path.join(self._source_subfolder, "sys", "time.h"))
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING*", src="sources", dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["gcrypt"]
