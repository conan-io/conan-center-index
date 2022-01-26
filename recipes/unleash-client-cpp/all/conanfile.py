from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class UnleashConan(ConanFile):
    name = "unleash-client-cpp"
    homepage = "https://github.com/aruizs/unleash-client-cpp/"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Unleash Client SDK for C++ projects."
    topics = ("unleash", "feature", "flag", "toggle")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake", "cmake_find_package"
    exports_sources = "CMakeLists.txt", "patches/**"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    requires = (
        "cpr/1.7.2",
        "nlohmann_json/3.10.5",
    )

    build_requires = "cmake/3.21.0"

    _cmake = None

    _compilers_min_version = {
        "msvc": "19.10",
        "Visual Studio": "15",  # Should we check toolset?
        "gcc": "7.0.0",
        "clang": "4.0",
        "apple-clang": "3.8",
        "intel": "17",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _check_compiler_version(self):
        compiler = str(self.settings.compiler)
        version = tools.Version(self.settings.compiler.version)
        if version < self._compilers_min_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a %s version greater than %s" % (self.name, compiler, self._compilers_min_version[compiler]))

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 17)
        self._check_compiler_version()

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["ENABLE_TESTING"] = False
        self._cmake.definitions["ENABLE_TEST_COVERAGE"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["unleash"]
        self.cpp_info.names["cmake_find_package"] = "unleash"
