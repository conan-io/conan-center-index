from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class GameNetworkingSocketsConan(ConanFile):
    name = "game-networking-sockets"
    description = "GameNetworkingSockets is a basic transport layer for games."
    topics = ("networking", "game-development")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ValveSoftware/GameNetworkingSockets"
    license = "BSD 3-Clause"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"

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
        if self.options.encryption == "bcrypt" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("bcrypt is only valid on Windows")

    def requirements(self):
        self.requires("protobuf/3.17.1")
        if self.options.encryption == "openssl":
            self.requires("openssl/1.1.1k")
        elif self.options.encryption == "libsodium":
            self.requires("libsodium/1.0.18")
        elif self.options.encryption == "bcrypt":
            # self.requires("libxcrypt/4.4.25")
            pass
    
    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)


    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["GAMENETWORKINGSOCKETS_BUILD_EXAMPLES"] = "OFF"
        self._cmake.definitions["GAMENETWORKINGSOCKETS_BUILD_TESTS"] = "OFF"
        crypto = {"openssl": "OpenSSL", "libsodium": "libsodium", "bcrypt": "BCrypt"}
        self._cmake.definitions["USE_CRYPTO"] = crypto[str(self.options.encryption)]
        crypto25519 = {"openssl": "OpenSSL", "libsodium": "libsodium", "bcrypt": "Reference"}
        self._cmake.definitions["USE_CRYPTO25519"] = crypto25519[str(self.options.encryption)]
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "GameNetworkingSockets"
        self.cpp_info.names["cmake_find_package_multi"] = "GameNetworkingSockets"
        self.cpp_info.names["pkg_config"] = "GameNetworkingSockets"
        self.cpp_info.includedirs.append(os.path.join("include", "GameNetworkingSockets"))
        self.cpp_info.libs = ["GameNetworkingSockets"]
        self.cpp_info.requires = ["protobuf::libprotobuf"]
        if self.options.encryption == "openssl":
            self.cpp_info.requires += ["openssl::crypto"]
        elif self.options.encryption == "libsodium":
            self.cpp_info.requires += ["libsodium::libsodium"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
        
