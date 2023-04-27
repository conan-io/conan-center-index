from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, load, rm, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os
import re

required_conan_version = ">=1.52.0"


class RestbedConan(ConanFile):
    name = "restbed"
    homepage = "https://github.com/Corvusoft/restbed"
    description = "Corvusoft's Restbed framework brings asynchronous RESTful functionality to C++14 applications."
    topics = ("restful", "server", "client", "json", "http", "ssl", "tls")
    url = "https://github.com/conan-io/conan-center-index"
    license = "AGPL-3.0-or-later", "LicenseRef-CPL"  # Corvusoft Permissive License (CPL)

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "ipc": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "ipc": False,
        "with_openssl": True,
    }

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "7",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        if self.settings.os in ("Windows", ):
            del self.options.ipc

    def validate(self):
        if getattr(self.info.settings.compiler, "cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
            if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support."
                )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("asio/1.27.0")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_SSL"] = self.options.with_openssl
        tc.variables["BUILD_IPC"] = self.options.get_safe("ipc", False)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if not self.options.shared:
            # Remove __declspec(dllexport) and __declspec(dllimport)
            for root, _, files in os.walk(self.source_folder):
                for file in files:
                    if os.path.splitext(file)[1] in (".hpp", ".h"):
                        full_path = os.path.join(root, file)
                        data = load(self, full_path)
                        data, _ = re.subn(r"__declspec\((dllexport|dllimport)\)", "", data)
                        save(self, full_path, data)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        libname = "restbed"
        if self.settings.os in ("Windows", ) and self.options.shared:
            libname += "-shared"
        self.cpp_info.libs = [libname]

        if self.settings.os in ("FreeBSD", "Linux", ):
            self.cpp_info.system_libs.extend(["dl", "m"])
        elif self.settings.os in ("Windows", ):
            self.cpp_info.system_libs.append("mswsock")
