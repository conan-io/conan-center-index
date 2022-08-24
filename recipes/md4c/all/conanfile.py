from conan import ConanFile, tools
from conans import CMake
import functools
import os

required_conan_version = ">=1.33.0"

class Md4cConan(ConanFile):
    name = "md4c"
    description = "C Markdown parser. Fast. SAX-like interface. Compliant to CommonMark specification."
    license = "MIT"
    topics = ("markdown-parser", "markdown")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mity/md4c"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "encoding": ["utf-8", "utf-16", "ascii"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "encoding": "utf-8",
    }
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os != "Windows" and self.options.encoding == "utf-16":
            raise tools.ConanInvalidConfiguration("utf-16 options is not supported on non-Windows platforms")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)

        if self.options.encoding == "utf-16":
            cmake.definitions["CONAN_C_FLAGS"] = "-DMD4C_USE_UTF16"
        elif self.options.encoding == "ascii":
            cmake.definitions["CONAN_C_FLAGS"] = "-DMD4C_USE_ASCII"

        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["md4c", "md4c-html",]

        if self.options.encoding == "utf-16":
            self.cpp_info.defines.append("MD4C_USE_UTF16")
