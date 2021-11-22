from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.42.1"


class Antlr4CppRuntimeConan(ConanFile):
    name = "antlr4-cppruntime"
    homepage = "https://github.com/antlr/antlr4/tree/master/runtime/Cpp"
    description = "C++ runtime support for ANTLR (ANother Tool for Language Recognition)"
    topics = ("antlr", "parser", "runtime")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    short_paths = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _main_code_subfolder(self):
        return "antlr4-" + self.version

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = os.path.join( self._main_code_subfolder , "runtime", "Cpp" )
        os.rename(extracted_dir, self._source_subfolder)

    def requirements(self):
        if self.settings.os in ("FreeBSD", "Linux"):
            self.requires("libuuid/1.0.3")

    def validate(self):
        if str(self.settings.arch).startswith("arm"):
            raise ConanInvalidConfiguration(f"arm architectures are not supported")
            # Need to deal with missing libuuid on Arm.
            # So far ANTLR delivers macOS binary package.

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("LICENSE.txt", src=self._main_code_subfolder, dst="licenses")

        self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so", dst="lib", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib*", dst="lib", keep_path=False)
        self.copy(pattern="*.dll", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ["include", os.path.join("include", "antlr4-runtime")]
