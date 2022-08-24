import os
from conans import CMake, ConanFile, tools

required_conan_version = ">=1.33.0"

class DuktapeConan(ConanFile):
    name = "duktape"
    license = "MIT"
    description = "Duktape is an embeddable Javascript engine, with a focus on portability and compact footprint."
    topics = ("javascript", "engine", "embeddable", "compact")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://duktape.org"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _cmake = None

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

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder) 

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        # Duktape has configure script with a number of options.
        # However it requires python 2 and PyYAML package
        # which is quite an unusual combination to have.
        # The most crucial option is --dll which just flips this define.
        if self.settings.os == "Windows" and self.options.shared:
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "src", "duk_config.h"),
                "#undef DUK_F_DLL_BUILD",
                "#define DUK_F_DLL_BUILD",
            )
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["duktape"]
        if not self.options.shared and str(self.settings.os) in (
            "Linux",
            "FreeBSD",
            "SunOS",
        ):
            self.cpp_info.system_libs = ["m"]
