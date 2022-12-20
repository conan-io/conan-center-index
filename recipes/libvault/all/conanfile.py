import os

from conan import ConanFile, Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime

required_conan_version = ">=1.53.0"


class LibvaultConan(ConanFile):
    name = "libvault"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/abedra/libvault"
    description = "A C++ library for Hashicorp Vault"
    topics = ("vault", "libvault", "secrets", "passwords")
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _mac_os_minimum_required_version(self):
        return "10.15"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("libcurl/7.86.0")
        self.requires("catch2/3.2.0")

    def validate(self):
        compiler = str(self.info.settings.compiler)
        compiler_version = Version(self.settings.compiler.version.value)

        minimum_compiler_version = {
            "Visual Studio": "19",
            "gcc": "8",
            "clang": "7.0",
            "apple-clang": "12",
        }

        minimum_cpp_standard = 17

        if compiler in minimum_compiler_version and \
           compiler_version < minimum_compiler_version[compiler]:
            raise ConanInvalidConfiguration(
                f"{self.name} requires a compiler that supports at least C++{minimum_cpp_standard}. "
                f"{compiler} {compiler_version} is not supported.")

        if compiler == "clang" and self.settings.compiler.libcxx in ["libstdc++", "libstdc++11"] and self.settings.compiler.version == "11":
            raise ConanInvalidConfiguration("clang 11 with libstdc++ is not supported due to old libstdc++ missing C++17 support")

        if is_apple_os(self):
            os_version = self.info.settings.get_safe("os.version")
            if os_version and Version(os_version) < self._mac_os_minimum_required_version:
                raise ConanInvalidConfiguration(
                    "Macos Mojave (10.14) and earlier cannot to be built because C++ standard library too old.")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, minimum_cpp_standard)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_TEST"] = "OFF"
        tc.variables["ENABLE_INTEGRATION_TEST"] = "OFF"
        tc.variables["ENABLE_COVERAGE"] = "OFF"
        tc.variables["LINK_CURL"] = "OFF"
        tc.variables["CMAKE_OSX_DEPLOYMENT_TARGET"] = self._mac_os_minimum_required_version
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.build_folder)
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["vault"]
        self.cpp_info.system_libs = ["m"]
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version).major == "8":
            self.cpp_info.system_libs.append("stdc++fs")
        # TODO: Remove after Conan 2.0
        self.cpp_info.names["cmake_find_package"] = "libvault"
        self.cpp_info.names["cmake_find_package_multi"] = "libvault"

        self.cpp_info.set_property("pkg_config_name", "vault")
        self.cpp_info.set_property("cmake_file_name", "libvault")
        self.cpp_info.set_property("cmake_target_name", "libvault::libvault")
