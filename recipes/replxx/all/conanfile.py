import os
from from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.33.0"

class ReplxxConan(ConanFile):
    name = "replxx"
    description = """
    A readline and libedit replacement that supports UTF-8,
    syntax highlighting, hints and Windows and is BSD licensed.
    """
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AmokHuginnsson/replxx"
    topics = ("readline", "libedit", "UTF-8")
    license = "BSD-3-Clause"
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

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["REPLXX_BuildExamples"] = False
            self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
            self._cmake.configure()
        return self._cmake

    def build(self):
        if tools.Version(self.version) < "0.0.3":
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "src", "io.cxx"),
                "#include <array>\n",
                "#include <array>\n#include <stdexcept>\n"
            )
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", dst='licenses', src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "m"]
        if not self.options.shared:
            self.cpp_info.defines.append("REPLXX_STATIC")
        self.cpp_info.filenames["cmake_find_package"] = "replxx"
        self.cpp_info.filenames["cmake_find_package_multi"] = "replxx"
