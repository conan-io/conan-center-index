from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class GameNetworkingSocketsConan(ConanFile):
    name = "gamenetworkingsockets"
    description = "GameNetworkingSockets is a basic transport layer for games."
    topics = ("networking", "game-development")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ValveSoftware/GameNetworkingSockets"
    license = "BSD-3-Clause"
    generators = "cmake", "pkg_config"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt", "patches/**"]

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "encryption": ["openssl", "libsodium", "bcrypt"]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "encryption": "openssl"
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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 11)

        if self.options.encryption == "bcrypt" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("bcrypt is only valid on Windows")

    def build_requirements(self):
        self.build_requires("protobuf/3.17.1")

    def requirements(self):
        self.requires("protobuf/3.17.1")
        if self.options.encryption == "openssl":
            self.requires("openssl/1.1.1l")
        elif self.options.encryption == "libsodium":
            self.requires("libsodium/1.0.18")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["GAMENETWORKINGSOCKETS_BUILD_EXAMPLES"] = False
        self._cmake.definitions["GAMENETWORKINGSOCKETS_BUILD_TESTS"] = False
        self._cmake.definitions["Protobuf_USE_STATIC_LIBS"] = not self.options["protobuf"].shared
        crypto = {"openssl": "OpenSSL", "libsodium": "libsodium", "bcrypt": "BCrypt"}
        self._cmake.definitions["USE_CRYPTO"] = crypto[str(self.options.encryption)]
        crypto25519 = {"openssl": "OpenSSL", "libsodium": "libsodium", "bcrypt": "Reference"}
        self._cmake.definitions["USE_CRYPTO25519"] = crypto25519[str(self.options.encryption)]
        if self.options.encryption == "openssl":
            self._cmake.definitions["OPENSSL_NEW_ENOUGH"] = True
            self._cmake.definitions["OPENSSL_HAS_25519_RAW"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "GameNetworkingSockets"
        self.cpp_info.names["cmake_find_package_multi"] = "GameNetworkingSockets"
        self.cpp_info.names["pkg_config"] = "GameNetworkingSockets"
        self.cpp_info.includedirs.append(os.path.join("include", "GameNetworkingSockets"))
        if self.options.shared:
            self.cpp_info.libs = ["GameNetworkingSockets"]
        else:
            self.cpp_info.libs = ["GameNetworkingSockets_s"]
            self.cpp_info.defines = ["STEAMNETWORKINGSOCKETS_STATIC_LINK"]

        self.cpp_info.requires = ["protobuf::libprotobuf"]
        if self.options.encryption == "openssl":
            self.cpp_info.requires += ["openssl::crypto"]
        elif self.options.encryption == "libsodium":
            self.cpp_info.requires += ["libsodium::libsodium"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "crypt32", "winmm"]
            if self.options.encryption == "bcrypt":
                self.cpp_info.system_libs += ["bcrypt"]
        
