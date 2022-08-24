import os
import glob
from conan import ConanFile, tools
from conans import CMake


class IqaConan(ConanFile):
    name = "iqa"
    description = "Image Quality Analysis Library"
    license = "BSD-3-Clause"
    topics = ("conan", "iqa", "image", "quality", "analysis")
    homepage = "https://github.com/tjdistler/iqa"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    _cmake = None

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
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('iqa-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

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
        content_lines = open(os.path.join(self._source_subfolder, "include", "iqa.h")).readlines()
        license_content = []
        for i in range(1, 31):
            license_content.append(content_lines[i][3:-1])
        tools.files.save(self, "LICENSE", "\n".join(license_content))

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self._extract_license()
        self.copy("LICENSE", dst="licenses")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
