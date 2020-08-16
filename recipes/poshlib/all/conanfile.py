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

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_license(self):
        with open(os.path.join(self._source_subfolder, "posh.h")) as f:
            content_lines = f.readlines()
        license_content = []
        for i in range(27, 59):
            license_content.append(content_lines[i][-1])
        tools.save("LICENSE", "\n".join(license_content))

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self._extract_license()
        self.copy(pattern="LICENSE", dst="licenses")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == 'Windows' and self.options.shared:
            self.cpp_info.defines.append("POSH_DLL")
