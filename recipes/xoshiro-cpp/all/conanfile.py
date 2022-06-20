from conans import ConanFile, tools

required_conan_version = ">=1.33.0"


class XoshiroCppConan(ConanFile):
    name = "xoshiro-cpp"
    description = "Header-only Xoshiro/Xoroshiro PRNG wrapper library for modern C++ (C++17/C++20)"
    topics = ("prng", "xoshiro", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Reputeless/Xoshiro-cpp"
    license = "MIT"
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

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy("*.hpp", dst="include/xoshiro-cpp",
                  src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
