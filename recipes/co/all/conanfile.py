from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class CoConan(ConanFile):
    name = "co"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/idealvin/co"
    license = "MIT"
    description = "A go-style coroutine library in C++11 and more."
    topics = ("co", "coroutine", "c++11")

    deprecated = "cocoyaxi"

    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake", "cmake_find_package"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libcurl": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libcurl": False,
        "with_openssl": False,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_libcurl:
            self.requires("libcurl/7.79.1")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1l")

    def build_requirements(self):
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            #  The OSX_ARCHITECTURES target property is now respected for the ASM language
            self.build_requires("cmake/3.20.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if not self.options.shared:
            self._cmake.definitions["FPIC"] = self.options.get_safe("fPIC", False)
        runtime = self.settings.get_safe("compiler.runtime")
        if runtime:
            self._cmake.definitions["STATIC_VS_CRT"] = "MT" in runtime
        self._cmake.definitions["WITH_LIBCURL"] = self.options.with_libcurl
        self._cmake.definitions["WITH_OPENSSL"] = self.options.with_openssl
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["co"]
        self.cpp_info.names["cmake_find_package"] = "co"
        self.cpp_info.names["cmake_find_package_multi"] = "co"

    def validate(self):
        if self.options.with_libcurl:
            if not self.options.with_openssl:
                raise ConanInvalidConfiguration(f"{self.name} requires with_openssl=True when using with_libcurl=True")
            if self.options["libcurl"].with_ssl != "openssl":
                raise ConanInvalidConfiguration(f"{self.name} requires libcurl:with_ssl='openssl' to be enabled")
            if not self.options["libcurl"].with_zlib:
                raise ConanInvalidConfiguration(f"{self.name} requires libcurl:with_zlib=True to be enabled")
