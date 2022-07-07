from conans import ConanFile, CMake, tools
import shutil

required_conan_version = ">=1.33.0"


class CppcmsConan(ConanFile):
    name = "cppcms"
    homepage = "http://cppcms.com"
    description = "High Performance C++ Web Framework"
    topics = ("web", "framework")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
    }
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def requirements(self):
        self.requires("pcre/8.45")
        self.requires("icu/71.1")
        self.requires("boost/1.79.0")
        self.requires("zlib/1.2.12")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1o")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions['DISABLE_SHARED'] = not self.options.shared
        self._cmake.definitions['DISABLE_STATIC'] = self.options.shared
        self._cmake.definitions['DISABLE_GCRYPT'] = True
        self._cmake.definitions['DISABLE_OPENSSL'] = not self.options.with_openssl
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING.TXT", dst="licenses", src=self._source_subfolder)
        self.copy("MIT.TXT", dst="licenses", src=self._source_subfolder)
        self.copy("THIRD_PARTY_SOFTWARE.TXT", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "cppcms"
        self.cpp_info.names["cmake_find_package_multi"] = "cppcms"
        self.cpp_info.names["pkg_config"] = "cppcms"
        self.cpp_info.libs = self.collect_libs()
