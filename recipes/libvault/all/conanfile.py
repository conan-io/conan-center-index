import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.54.0"


class LibvaultConan(ConanFile):
    name = "libvault"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/abedra/libvault"
    description = "A C++ library for Hashicorp Vault"
    topics = ("vault", "libvault", "secrets", "passwords")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _mac_os_minimum_required_version(self):
        return "10.15"

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "7.0",
            "apple-clang": "12",
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
        # public header VaultClient.h includes curl/curl.h and use several functions
        self.requires("libcurl/[>=7.78.0 <9]", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.settings.compiler == "clang" and self.settings.compiler.libcxx in ["libstdc++", "libstdc++11"] and self.settings.compiler.version == "11":
            raise ConanInvalidConfiguration("clang 11 with libstdc++ is not supported due to old libstdc++ missing C++17 support")

        if is_apple_os(self):
            os_version = self.settings.get_safe("os.version")
            if os_version and Version(os_version) < self._mac_os_minimum_required_version:
                raise ConanInvalidConfiguration(
                    "Macos Mojave (10.14) and earlier cannot to be built because C++ standard library too old.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_TEST"] = False
        tc.variables["ENABLE_INTEGRATION_TEST"] = False
        tc.variables["ENABLE_COVERAGE"] = False
        tc.variables["LINK_CURL"] = True
        tc.variables["CMAKE_OSX_DEPLOYMENT_TARGET"] = self._mac_os_minimum_required_version

        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        # INFO: https://github.com/abedra/libvault/pull/123
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                         "target_link_libraries(vault curl)",
                         "target_link_libraries(vault CURL::libcurl)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["vault"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version).major == "8":
            self.cpp_info.system_libs.append("stdc++fs")

        self.cpp_info.set_property("pkg_config_name", "vault")
        self.cpp_info.set_property("cmake_file_name", "libvault")
        self.cpp_info.set_property("cmake_target_name", "libvault::libvault")
