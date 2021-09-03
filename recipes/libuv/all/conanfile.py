from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class libuvConan(ConanFile):
    name = "libuv"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libuv.org"
    description = "A multi-platform support library with a focus on asynchronous I/O"
    topics = ("libuv", "asynchronous", "io", "networking", "multi-platform", "conan-recipe")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"
    exports_sources = [
        "CMakeLists.txt",
        "patches/*"
    ]

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
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            if tools.Version(self.settings.compiler.version) < "14":
                raise ConanInvalidConfiguration("Visual Studio 2015 or higher required")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LIBUV_BUILD_TESTS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libuv"
        self.cpp_info.libs = ["uv" if self.options.shared else "uv_a"]
        if self.options.shared:
            self.cpp_info.defines = ["USING_UV_SHARED=1"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "pthread", "rt"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["iphlpapi", "psapi", "userenv", "ws2_32"]
