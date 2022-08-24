from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class XoshiroCppConan(ConanFile):
    name = "xoshiro-cpp"
    description = "Header-only Xoshiro/Xoroshiro PRNG wrapper library for modern C++ (C++17/C++20)"
    license = "MIT"
    homepage = "https://github.com/Reputeless/Xoshiro-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("prng", "xoshiro", "header-only")
    settings = "arch", "build_type", "compiler", "os"
    generators = "cmake"
    no_copy_source = True

    @property
    def _minimum_compilers_version(self):
        return {
            "apple-clang": "10",
            "clang": "6",
            "gcc": "7",
            "Visual Studio": "16"
        }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 17

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.build.check_min_cppstd(self, self, self._minimum_cpp_standard)

        compiler = self.settings.compiler
        try:
            min_version = self._minimum_compilers_version[str(compiler)]
            if tools.Version(compiler.version) < min_version:
                msg = (
                    "{} requires C++{} features which are not supported by compiler {} {}."
                ).format(self.name, self._minimum_cpp_standard, compiler, compiler.version)
                raise ConanInvalidConfiguration(msg)
        except KeyError:
            msg = (
                "{} recipe lacks information about the {} compiler, "
                "support for the required C++{} features is assumed"
            ).format(self.name, compiler, self._minimum_cpp_standard)
            self.output.warn(msg)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("*.hpp", dst="include/xoshiro-cpp",
                  src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "xoshiro-cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "xoshiro-cpp"
