from conans import ConanFile, tools, CMake

required_conan_version = ">=1.33.0"


class farmhashConan(ConanFile):
    name = "farmhash"
    description = "A family of hash functions"
    topics = ("hash", "google", "family")
    license = "MIT"
    homepage = "https://github.com/google/farmhash"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "no_builtin_expect": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "no_builtin_expect": False
    }
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FARMHASH_NO_BUILTIN_EXPECT"] = self.options.no_builtin_expect
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.libs=["farmhash"]
