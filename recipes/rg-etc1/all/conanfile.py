import os
import glob
from conan import ConanFile, tools
from conan.tools.cmake import CMake


class RgEtc1Conan(ConanFile):
    name = "rg-etc1"
    description = "A performant, easy to use, and high quality 4x4 pixel block packer/unpacker for the ETC1."
    homepage = "https://github.com/richgel999/rg-etc1"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "etc1", "packer", "unpacker")
    license = "Zlib"
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

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('rg-etc1-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_license(self):
        with open(os.path.join(self._source_subfolder, "rg_etc1.h")) as f:
            content_lines = f.readlines()
        license_content = []
        for i in range(52, 75):
            license_content.append(content_lines[i][2:-1])
        tools.save("LICENSE", "\n".join(license_content))

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self._extract_license()
        self.copy(pattern="LICENSE", dst="licenses")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
