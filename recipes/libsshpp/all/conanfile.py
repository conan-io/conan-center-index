from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0"


class LibsshppConan(ConanFile):
    name = "libsshpp"
    description = "Modern C++17 wrapper around libssh"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/slightlabs/libsshpp"
    topics = ("ssh", "libssh", "cpp17", "wrapper")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
        "with_sftp": [True, False],
        "with_scp": [True, False],
        "with_server": [True, False],
        "with_forwarding": [True, False],
        "with_console": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
        "with_sftp": True,
        "with_scp": True,
        "with_server": True,
        "with_forwarding": True,
        "with_console": False,
    }

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "clang": "12",
            "apple-clang": "14",
            "msvc": "192",
            "Visual Studio": "16",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.header_only:
            self.options.rm_safe("fPIC")
            self.options.rm_safe("shared")
        elif self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires at least {self.settings.compiler} {minimum_version} for C++{self._min_cppstd}"
            )

    def requirements(self):
        # libssh 0.10.4 - 0.11.x per upstream README
        self.requires("libssh/[>=0.10.4 <0.12]", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBSSHPP_HEADER_ONLY"] = self.options.header_only
        tc.variables["LIBSSHPP_WITH_SFTP"] = self.options.with_sftp
        tc.variables["LIBSSHPP_WITH_SCP"] = self.options.with_scp
        tc.variables["LIBSSHPP_WITH_SERVER"] = self.options.with_server
        tc.variables["LIBSSHPP_WITH_FORWARDING"] = self.options.with_forwarding
        tc.variables["LIBSSHPP_WITH_CONSOLE"] = self.options.with_console
        tc.variables["LIBSSHPP_BUILD_EXAMPLES"] = False
        tc.variables["LIBSSHPP_BUILD_TESTS"] = False
        tc.variables["LIBSSHPP_INSTALL"] = True
        if not self.options.header_only:
            tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        if is_msvc(self):
            tc.cache_variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        if not self.options.header_only:
            cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "THIRD_PARTY_NOTICES.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        if self.options.header_only:
            # CMake disables the install target for header-only mode
            copy(self, "*",
                 src=os.path.join(self.source_folder, "include", "sshpp"),
                 dst=os.path.join(self.package_folder, "include", "sshpp"),
                 keep_path=False)
            copy(self, "*",
                 src=os.path.join(self.build_folder, "include", "sshpp"),
                 dst=os.path.join(self.package_folder, "include", "sshpp"),
                 keep_path=False)
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libsshpp")
        self.cpp_info.set_property("cmake_target_name", "libsshpp::libsshpp")
        self.cpp_info.set_property("cmake_target_aliases", ["libsshpp"])
        self.cpp_info.requires = ["libssh::libssh"]

        if self.options.header_only:
            self.cpp_info.bindirs = []
            self.cpp_info.libdirs = []
        else:
            self.cpp_info.libs = ["sshpp"]
            if not self.options.shared:
                self.cpp_info.defines.append("SSHPP_STATIC_DEFINE")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("pthread")
            if not self.options.shared and self.settings.os == "Windows":
                self.cpp_info.system_libs.extend(["ws2_32", "iphlpapi"])
