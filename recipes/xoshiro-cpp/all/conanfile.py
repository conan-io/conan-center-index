from conans import ConanFile, tools

required_conan_version = ">=1.33.0"


class XoshiroCppConan(ConanFile):
    name = "xoshiro-cpp"
    description = "Header-only Xoshiro/Xoroshiro PRNG wrapper library for modern C++ (C++17/C++20)"
    license = "MIT"
    homepage = "https://github.com/Reputeless/Xoshiro-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("prng", "xoshiro", "header-only")
    settings = "arch", "build_type", "compiler", "os"
    generators = "cmake", "cmake_find_package_multi"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 17

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
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
