from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class MBitsArgsConan(ConanFile):
    name = "mbits-args"
    description = "Small open-source library for program argument parser, inspired by Python's `argparse`, " \
                  "depending only on the standard library, with C++17 as minimum requirement."
    homepage = "https://github.com/mbits-libs/args"
    license = "MIT"
    topics = ("command-line", "commandline", "commandline-interface",
              "program-arguments", "argparse", "argparser", "argument-parsing")

    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"

    _cmake = None

    _compilers_minimum_version = {
        "gcc": "8",
        "clang": "7.0",
        "intel": "19",
        "Visual Studio": "16",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn(
                "mbits-args requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("mbits-args: Unsupported compiler: {}-{}; "
                                            "minimal version known to work is {}."
                                            .format(self.settings.compiler, self.settings.compiler.version, minimum_version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("args-{}".format(self.version),
                  self._source_subfolder)
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LIBARGS_TESTING"] = "OFF"
        self._cmake.definitions["LIBARGS_INSTALL"] = "ON"
        self._cmake.definitions["LIBARGS_SHARED"] = self.options.shared
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE",
                  "licenses", keep_path=False, src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["args"]
