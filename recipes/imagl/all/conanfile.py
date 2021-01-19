from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.32.0"


class ImaglConan(ConanFile):
    name = "imagl"
    license = "GPL-3.0-or-later"
    homepage = "https://github.com/Woazim/imaGL"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A lightweight library to load image for OpenGL application."
    topics = ("opengl", "texture", "image")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "with_png": [True, False]}
    default_options = {"shared": False, "fPIC": True, "with_png": True}
    generators = "cmake"
    exports_sources = "CMakeLists.txt"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "16.5",
            "clang": "10",
            "apple-clang": "11"
        }

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-v" + self.version, self._source_subfolder)

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 20)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("imagl requires C++20, which your compiler does not fully support.")
        else:
            self.output.warn("imagl requires C++20. Your compiler is unknown. Assuming it supports C++20.")

    def requirements(self):
        if self.options.with_png:
            self.requires("libpng/1.6.37")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["STATIC_LIB"] = not self.options.shared
        self._cmake.definitions["SUPPORT_PNG"] = self.options.with_png
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        debug_suffix = "d" if self.settings.build_type == "Debug" else ""
        static_suffix = "" if self.options.shared else "s"
        self.cpp_info.libs = ["imaGL{}{}".format(debug_suffix, static_suffix)]
        if not self.options.shared:
            self.cpp_info.defines = ["IMAGL_STATIC=1"]
