from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.gnu import PkgConfigDeps
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.microsoft import is_msvc
import os


required_conan_version = ">=2.1"


class Libfido2Conan(ConanFile):
    name = "libfido2"
    description = "Library for communication with FIDO2 devices over USB or NFC"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developers.yubico.com/libfido2/"
    topics = ("fido2", "webauthn", "yubikey")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "nfc_linux": [True, False],
        "use_winhello": [True, False],
    }

    default_options = {
        "shared": False,
        "nfc_linux": True,
        "use_winhello": True,
    }

    def config_options(self):
        if self.settings.os != "Linux":
            self.options.rm_safe("nfc_linux")

        if self.settings.os != "Windows":
            self.options.rm_safe("use_winhello")

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libcbor/0.14.0")
        self.requires("openssl/[>=3 <4]", transitive_headers=True)
        self.requires("zlib/[>=1.2.11 <2]")

        if self.settings.os == "Linux":
            self.requires("libudev/system")

    def build_requirements(self):
        if not is_msvc(self) and not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.1.0 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.cache_variables["BUILD_TESTS"] = False
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_MANPAGES"] = False
        tc.cache_variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.cache_variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.cache_variables["BUILD_TOOLS"] = False

        if self.settings.os == "Linux":
            tc.cache_variables["NFC_LINUX"] = bool(self.options.nfc_linux)

        if self.settings.os == "Windows":
            tc.cache_variables["USE_WINHELLO"] = bool(self.options.use_winhello)

        if is_msvc(self):
            cbor = self.dependencies["libcbor"].cpp_info
            crypto = self.dependencies["openssl"].cpp_info.components["crypto"]
            zlib = self.dependencies["zlib"].cpp_info

            deps = [
                ("CBOR", cbor),
                ("CRYPTO", crypto),
                ("ZLIB", zlib),
            ]

            for prefix, dep in deps:
                tc.cache_variables[f"{prefix}_INCLUDE_DIRS"] = dep.includedirs
                tc.cache_variables[f"{prefix}_LIBRARY_DIRS"] = dep.libdirs
                tc.cache_variables[f"{prefix}_LIBRARIES"] = dep.libs + dep.system_libs

        tc.generate()

        if not is_msvc(self):
            pkg_config = PkgConfigDeps(self)
            pkg_config.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        if self.settings.os == "Macos" and self.options.shared:
            fix_apple_shared_install_name(self)

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["fido2"]
        if self.settings.os == "Windows" and is_msvc(self) and not self.options.shared:
            self.cpp_info.libs = ["fido2_static"]

        self.cpp_info.set_property("cmake_file_name", "libfido2")
        self.cpp_info.set_property("cmake_target_name", "libfido2::libfido2")
        self.cpp_info.set_property("pkg_config_name", "libfido2")

        self.cpp_info.requires = [
            "libcbor::libcbor",
            "openssl::crypto",
            "zlib::zlib",
        ]

        if self.settings.os == "Linux":
            self.cpp_info.requires.append("libudev::libudev")

        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.system_libs.extend([
                    "wsock32", "ws2_32", "bcrypt", "setupapi", "hid"
                ])
            elif self.settings.os == "Macos":
                self.cpp_info.frameworks.extend(["CoreFoundation", "IOKit"])
