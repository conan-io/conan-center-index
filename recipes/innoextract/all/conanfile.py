import os
import functools
from conan import ConanFile, tools
from conans import CMake

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
        "boost/1.78.0",
        "xz_utils/5.2.5",
        "libiconv/1.16"
    )
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        os.remove(os.path.join(self._source_subfolder, 'cmake', 'FindLZMA.cmake'))
        os.remove(os.path.join(self._source_subfolder, 'cmake', 'Findiconv.cmake'))
        cmake = self._configure_cmake()
        cmake.build()

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        # Turn off static library detection, which is on by default on Windows.
        # This keeps the CMakeLists.txt from trying to detect static Boost
        # libraries and use Boost components for zlib and BZip2. Getting the
        # libraries via Conan does the correct thing without other assistance.
        cmake.definitions["USE_STATIC_LIBS"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_id(self):
        del self.info.settings.compiler
        self.info.requires.clear()

    def package_info(self):
        self.cpp_info.libdirs = []
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}"
                         .format(bindir))
        self.env_info.PATH.append(bindir)
