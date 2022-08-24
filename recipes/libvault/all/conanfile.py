from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
from conans.tools import Version
import os

required_conan_version = ">=1.33.0"


class LibvaultConan(ConanFile):
    name = "libvault"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/abedra/libvault"
    description = "A C++ library for Hashicorp Vault"
    topics = ("vault", "libvault", "secrets", "passwords")
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _mac_os_minimum_required_version(self):
        return "10.15"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libcurl/7.80.0")
        self.requires("catch2/2.13.7")

    def validate(self):
        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version.value)

        minimum_compiler_version = {
            "Visual Studio": "19",
            "gcc": "8",
            "clang": "7.0",
            "apple-clang": "12"
        }

        minimum_cpp_standard = 17

        if compiler in minimum_compiler_version and \
           compiler_version < minimum_compiler_version[compiler]:
            raise ConanInvalidConfiguration("{} requires a compiler that supports"
                                            " at least C++{}. {} {} is not"
                                            " supported."
                                            .format(self.name, minimum_cpp_standard, compiler, compiler_version))

        if compiler == "clang" and self.settings.compiler.libcxx in ["libstdc++", "libstdc++11"] and self.settings.compiler.version == "11":
            raise ConanInvalidConfiguration("clang 11 with libstdc++ is not supported due to old libstdc++ missing C++17 support")

        if tools.apple.is_apple_os(self, self.settings.os):
            os_version = self.settings.get_safe("os.version")
            if os_version and Version(os_version) < self._mac_os_minimum_required_version:
                raise ConanInvalidConfiguration(
                    "Macos Mojave (10.14) and earlier cannot to be built because C++ standard library too old.")

        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, minimum_cpp_standard)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["ENABLE_TEST"] = False
            self._cmake.definitions["ENABLE_INTEGRATION_TEST"] = False
            self._cmake.definitions["ENABLE_COVERAGE"] = False
            self._cmake.definitions["LINK_CURL"] = False
            # Set `-mmacosx-version-min` to enable C++17 standard library support.
            self._cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = self._mac_os_minimum_required_version
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self, self)
        self.cpp_info.names["cmake_find_package"] = "libvault"
        self.cpp_info.names["cmake_find_package_multi"] = "libvault"
        self.cpp_info.names["pkg_config"] = "vault"
