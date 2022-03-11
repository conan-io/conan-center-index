import os
import glob
from conans import ConanFile, CMake, tools


class PoshlibConan(ConanFile):
    name = "poshlib"
    description = "Posh is a software framework used in cross-platform software development."
    homepage = "https://github.com/PhilipLudington/poshlib"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "posh", "framework", "cross-platform")
    license = "BSD-2-Clause"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('poshlib-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "posh.h"),
                              "defined _ARM",
                              "defined _ARM || defined __arm64")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == 'Windows' and self.options.shared:
            self.cpp_info.defines.append("POSH_DLL")
