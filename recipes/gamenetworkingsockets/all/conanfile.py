import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.gnu import PkgConfigDeps

required_conan_version = ">=1.53.0"


class GameNetworkingSocketsConan(ConanFile):
    name = "gamenetworkingsockets"
    description = "GameNetworkingSockets is a basic transport layer for games."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ValveSoftware/GameNetworkingSockets"
    topics = ("networking", "game-development")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "encryption": ["openssl", "libsodium", "bcrypt"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "encryption": "openssl",
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("protobuf/3.21.12")
        if self.options.encryption == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        elif self.options.encryption == "libsodium":
            self.requires("libsodium/cci.20220430")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

        if self.options.encryption == "bcrypt" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("bcrypt is only valid on Windows")

    def build_requirements(self):
        self.tool_requires("protobuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()
        venv = VirtualRunEnv(self)
        venv.generate(scope="build")

        tc = CMakeToolchain(self)
        tc.variables["GAMENETWORKINGSOCKETS_BUILD_EXAMPLES"] = False
        tc.variables["GAMENETWORKINGSOCKETS_BUILD_TESTS"] = False
        tc.variables["Protobuf_USE_STATIC_LIBS"] = not self.dependencies["protobuf"].options.shared
        tc.variables["Protobuf_IMPORT_DIRS"] = os.path.join(self.source_folder, "src", "common").replace("\\", "/")
        crypto = {
            "openssl": "OpenSSL",
            "libsodium": "libsodium",
            "bcrypt": "BCrypt",
        }
        tc.variables["USE_CRYPTO"] = crypto[str(self.options.encryption)]
        crypto25519 = {
            "openssl": "OpenSSL",
            "libsodium": "libsodium",
            "bcrypt": "Reference",
        }
        tc.variables["USE_CRYPTO25519"] = crypto25519[str(self.options.encryption)]
        if self.options.encryption == "openssl":
            tc.variables["OPENSSL_NEW_ENOUGH"] = True
            tc.variables["OPENSSL_HAS_25519_RAW"] = True
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()

    def _patch_sources(self):
        # Disable MSVC runtime override
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "configure_msvc_runtime()", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "GameNetworkingSockets")
        self.cpp_info.set_property("cmake_target_name", "GameNetworkingSockets::GameNetworkingSockets")
        self.cpp_info.set_property("pkg_config_name", "GameNetworkingSockets")
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
            self.cpp_info.system_libs = ["ws2_32", "crypt32", "winmm", "iphlpapi"]
            if self.options.encryption == "bcrypt":
                self.cpp_info.system_libs += ["bcrypt"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "GameNetworkingSockets"
        self.cpp_info.names["cmake_find_package_multi"] = "GameNetworkingSockets"
