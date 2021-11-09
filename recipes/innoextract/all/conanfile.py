import os
import shutil
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class InnoextractConan(ConanFile):
    name = "innoextract"
    description = "Extract contents of Inno Setup installers"
    license = "innoextract License"
    topics = ("inno-setup", "decompression")
    homepage = "https://constexpr.org/innoextract/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    requires = (
        ("boost/1.78.0", "private"),
        ("xz_utils/5.2.5", "private"),
        ("libiconv/1.16", "private")
    )
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        shutil.rmtree(os.path.join(self.package_folder, "share"))

    def package_id(self):
        del self.info.settings.compiler
        self.info.requires.clear()

    def package_info(self):
        self.cpp_info.libdirs = []
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}"
                         .format(bindir))
        self.env_info.PATH.append(bindir)
