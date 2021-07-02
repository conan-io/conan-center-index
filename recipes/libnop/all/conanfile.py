from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os


class LibnopConan(ConanFile):
    name = "libnop"
    description = "libnop is a header-only library for serializing and " \
                  "deserializing C++ data types without external code " \
                  "generators or runtime support libraries."
    license = "Apache-2.0"
    topics = ("conan", "libnop", "header-only", "serializer")
    homepage = "https://github.com/google/libnop"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)
        compiler = self.settings.compiler
        compiler_version = tools.Version(compiler.version)
        if (compiler == "gcc" and compiler_version < "5") or \
           (compiler == "Visual Studio" and compiler_version < "15"):
            raise ConanInvalidConfiguration("libnop doesn't support {} {}".format(str(compiler), compiler.version))

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("libnop-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
