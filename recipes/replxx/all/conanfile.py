import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class ReplxxConan(ConanFile):
    name = "replxx"
    description = """
    A readline and libedit replacement that supports UTF-8,
    syntax highlighting, hints and Windows and is BSD licensed.
    """
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AmokHuginnsson/replxx"
    topics = ("conan", "readline", "libedit", "UTF-8")
    license = "BSD"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
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
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
        self._cmake.definitions["REPLXX_BUILD_EXAMPLES"] = False
        self._cmake.definitions["REPLXX_BUILD_PACKAGE"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", dst='licenses', src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        if tools.os_info.is_linux:
            self.cpp_info.libs.append("pthread")
