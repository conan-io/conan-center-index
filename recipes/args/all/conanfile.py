from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class ArgsConan(ConanFile):
    name = "args"
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        compiler = str(self.settings.compiler)
        if compiler in self._working_compilers:
            working_compiler = self._working_compilers[compiler]
            current_compiler = ArgsConan.Version(
                str(self.settings.compiler.version))
            if working_compiler > current_compiler:
                msg = f"args library requires {compiler} version to be at least " \
                      f"{working_compiler}; this configuration uses version {current_compiler}"
                raise ConanInvalidConfiguration(msg)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version),
                  self._source_subfolder)
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        gen = CMake(self)
        gen.definitions["LIBARGS_TESTING"] = "OFF"
        gen.definitions["LIBARGS_INSTALL"] = "ON"
        gen.definitions["LIBARGS_SHARED"] = "ON" if self.options.shared else "OFF"
        gen.configure(source_folder=self._source_subfolder)
        return gen

    def build(self):
        gen = self._configure_cmake()
        gen.build()

    def package(self):
        gen = self._configure_cmake()
        gen.install()
        self.copy("LICENSE",
                  "licenses", keep_path=False, src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["args"]

    class Version(object):
        def __init__(self, value: str):
            self.components = value.split('.')

        def __str__(self): return '.'.join(self.components)

        @staticmethod
        def _comp(left_s, right_s):
            try:
                left_n = int(left_s)
                right_n = int(right_s)
                return left_n - right_n
            except ValueError:
                if left_s < right_s:
                    return -1
                if left_s > right_s:
                    return 1
                return 0

        def comp(self, rhs):
            items = min(len(self.components), len(rhs.components))
            for index in range(items):
                left_s = self.components[index]
                right_s = rhs.components[index]
                comp = ArgsConan.Version._comp(left_s, right_s)
                if comp != 0:
                    return comp

            return len(self.components) - len(rhs.components)

        def __lt__(self, rhs): return self.comp(rhs) < 0
        def __le__(self, rhs): return self.comp(rhs) <= 0
        def __gt__(self, rhs): return self.comp(rhs) > 0
        def __ge__(self, rhs): return self.comp(rhs) >= 0

    _working_compilers = {
        "gcc": Version("8"),
        "clang": Version("8"),
        "intel": Version("19"),
        "Visual Studio": Version("16"),
    }
