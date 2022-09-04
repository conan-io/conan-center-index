from conans import ConanFile, tools

required_conan_version = ">=1.33.0"

class FastPRNGConan(ConanFile):
    name = "fastprng"
    description = "FAST 32/64 bit PRNG (pseudo-random generator), highly optimized, based on xoshiro* / xoroshiro*, xorshift and other Marsaglia algorithms."
    topics = ("random", "prng", "xorshift", "xoshiro", )
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/BrutPitt/fastPRNG"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake",
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("license.txt", "licenses", self._source_subfolder)
        self.copy("*.h", "include", self._source_subfolder)
