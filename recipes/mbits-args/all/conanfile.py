from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
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
    exports_sources = "CMakeLists.txt"

    _cmake = None

    _compilers_minimum_version = {
        "gcc": "8",
        "clang": "7.0",
        "Visual Studio": "16",
        "apple-clang": "10.0",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

            if self.settings.compiler == "Visual Studio" and "MT" in str(self.settings.compiler.runtime):
                raise ConanInvalidConfiguration(
                    "mbits-args: combining shared library with private C++ "
                    "library (MT/MTd) is not supported.")

        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, "17")

        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn(
                "mbits-args requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif tools.scm.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("mbits-args: Unsupported compiler: {} {}; "
                                            "minimal version known to work is {}."
                                            .format(self.settings.compiler, self.settings.compiler.version, minimum_version))
        elif str(self.settings.compiler) == "clang" and tools.scm.Version(self.settings.compiler.version) < "8":
            libcxx = self.settings.compiler.get_safe("libcxx")
            if libcxx and str(libcxx) == "libc++":
                raise ConanInvalidConfiguration("mbits-args: Unsupported compiler: clang {} with libc++;\n"
                                                "minimal version known to work is either clang 8 with "
                                                "libc++ or clang {} with libstdc++/libstdc++11."
                                                .format(self.settings.compiler.version, minimum_version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("args-{}".format(self.version),
                  self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LIBARGS_TESTING"] = False
        self._cmake.definitions["LIBARGS_INSTALL"] = True
        self._cmake.definitions["LIBARGS_SHARED"] = self.options.shared
        self._cmake.configure()
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
        self.cpp_info.filenames["cmake_find_package"] = "args"
        self.cpp_info.filenames["cmake_find_package_multi"] = "args"
        self.cpp_info.names["cmake_find_package"] = "mbits"
        self.cpp_info.names["cmake_find_package_multi"] = "mbits"
        self.cpp_info.components["libargs"].names["cmake_find_package"] = "args"
        self.cpp_info.components["libargs"].names["cmake_find_package_multi"] = "args"
        self.cpp_info.components["libargs"].libs = tools.files.collect_libs(self, self)

        # FIXME: CMake imported target shouldn't be namespaced (requires https://github.com/conan-io/conan/issues/7615)
        # https://github.com/mbits-libs/args/blob/72f5f2b87ae39f26638a585fa4ad0b96b4152ae6/CMakeLists.txt#L152
