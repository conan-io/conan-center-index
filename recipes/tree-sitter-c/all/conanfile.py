from conan import ConanFile, tools
from conans import CMake
import functools
import os

required_conan_version = ">=1.33.0"


class TreeSitterCConan(ConanFile):
    name = "tree-sitter-c"
    description = "C grammar for tree-sitter."
    topics = ("parser", "grammar", "tree", "c", "ide")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tree-sitter/tree-sitter-c"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    generators = "cmake", "cmake_find_package_multi"
    exports_sources = "CMakeLists.txt"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("tree-sitter/0.20.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def _patch_sources(self):
        if not self.options.shared:
            tools.files.replace_in_file(self, 
                os.path.join(self._source_subfolder, "src", "parser.c"),
                "__declspec(dllexport)", ""
            )

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["tree-sitter-c"]
