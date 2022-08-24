from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.40.0"


class OfeliConan(ConanFile):
    name = "ofeli"
    description = "An Object Finite Element Library"
    topics = ("finite-element", "finite-element-library",
              "finite-element-analysis", "finite-element-solver")
    license = "LGPL-3.0-or-later"
    homepage = "http://ofeli.org/index.html"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _doc_folder(self):
        return os.path.join(
            self._source_subfolder,
            "doc"
        )

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                "Ofeli is just supported for Linux")
        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration(
                "Ofeli is just supported for GCC")
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration(
                "Ofeli supports only libstdc++'s new ABI")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure(args=["--enable-%s" % ("release"
                                  if self.settings.build_type == "Release"
                                  else "debug")])
        return self._autotools

    def build(self):
        with tools.files.chdir(self, self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("*.h", dst="include",
                  src=os.path.join(self._source_subfolder, "include"))
        self.copy("*libofeli.a", dst="lib",
                  src=os.path.join(self._source_subfolder, "src"))
        self.copy("*.md", dst="res",
                  src=os.path.join(self._source_subfolder, "material"))
        self.copy("COPYING", dst="licenses", src=self._doc_folder)

    def package_info(self):
        self.cpp_info.libs = ["ofeli"]
        self.env_info.OFELI_PATH_MATERIAL.append(
            os.path.join(self.package_folder, "res"))
