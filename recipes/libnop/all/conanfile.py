from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibnopConan(ConanFile):
    name = "libnop"
    description = "libnop is a header-only library for serializing and " \
                  "deserializing C++ data types without external code " \
                  "generators or runtime support libraries."
    license = "Apache-2.0"
    topics = ("libnop", "header-only", "serializer")
    homepage = "https://github.com/google/libnop"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 14)
        compiler = self.settings.compiler
        compiler_version = tools.scm.Version(compiler.version)
        if (compiler == "gcc" and compiler_version < "5") or \
           (compiler == "Visual Studio" and compiler_version < "15"):
            raise ConanInvalidConfiguration("libnop doesn't support {} {}".format(str(compiler), compiler.version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
