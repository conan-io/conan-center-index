from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class ArgparseConan(ConanFile):
    name = "argparse"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/p-ranav/argparse"
    topics = ("conan", "argparse", "argument", "parsing")
    license = "MIT"
    description = "Argument Parser for Modern C++"
    generators = "cmake"

    settings = "compiler"

    exports_sources = ["CMakeLists.txt"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _compiler_required_cpp17 = {
        "gcc": "7",
        "clang": "5",
        "Visual Studio": "15",
        "apple-clang": "10",
    }

    def configure(self):
        if self.settings.compiler.cppstd and self.settings.compiler.cppstd in ("98", "gnu98", "11", "gnu11", "14", "gnu14"):
            raise ConanInvalidConfiguration("This package requires C++17")
        try:
            minimum_required_compiler_version = self._compiler_required_cpp17[str(self.settings.compiler)]
            if tools.Version(self.settings.compiler.version) < minimum_required_compiler_version:
                raise ConanInvalidConfiguration("This package requires c++17 support. The current compiler does not support it.")
        except KeyError:
            self.output.info("This recipe has no support for the current compiler. Please consider adding it.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("argparse-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.includedirs = ["include", os.path.join("include", "argparse")]
