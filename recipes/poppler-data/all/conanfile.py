from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class PopplerDataConan(ConanFile):
    name = "poppler-data"
    description = "encoding files for use with poppler, enable CJK and Cyrrilic"
    homepage = "https://poppler.freedesktop.org/"
    topics = "conan", "poppler", "pdf", "rendering"
    license = "GPL-2.0-or-later", "adobe", "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("poppler-data-{}".format(self.version), self._source_subfolder)

    @property
    def _datadir(self):
        return os.path.join(self.package_folder, "bin")

    def _configure_cmake(self):
        # FIXME: USE_CMS
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["datadir"] = self._datadir
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patchdata in self.conan_data["patches"][self.version]:
            tools.patch(**patchdata)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self._datadir, "pkgconfig"))

        # Create a dummy header to circumvent CI
        tools.save(os.path.join(self.package_folder, "include", "_dummy.h"), "")

    def package_id(self):
        self.info.header_only()

    def _poppler_datadir(self):
        return os.path.join(self._datadir, "poppler")

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "poppler-data"
        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = []
        self.user_info.datadir = self._poppler_datadir
        self.cpp_info.defines = ["POPPLER_DATADIR={}".format(self._poppler_datadir)]
