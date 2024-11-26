from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.files import get, copy, apply_conandata_patches, export_conandata_patches, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"

class ZoeConan(ConanFile):
    name = "zoe"
    description = "A multi-protocol, multi-threaded, resumable, cross-platform, open source, C++ file download library."
    license = "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/winsoft666/zoe"
    topics = ("curl", "download", "file", "ftp", "multithreading", "http", "libcurl", "rate-limit")
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

    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("openssl/[>=1.1 <4]", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, "11")
        if self.info.settings.compiler == "apple-clang" and Version(self.info.settings.compiler.version) < "12.0":
            raise ConanInvalidConfiguration(f"{self.ref} can not build on apple-clang < 12.0.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ZOE_BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["ZOE_USE_STATIC_CRT"] = is_msvc_static_runtime(self)
        tc.variables["ZOE_BUILD_TESTS"] = False
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _apply_patches(self):
        apply_conandata_patches(self)
        # Remove hardcoded CMAKE_CXX_STANDANRD in newer versions
        if Version(self.version) >= "3.2":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "set (CMAKE_CXX_STANDARD 11)",
                            "")

    def build(self):
        self._apply_patches()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        libname = "zoe" if self.options.shared else "zoe-static"
        libpostfix = "-d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"{libname}{libpostfix}"]

        if self.options.shared:
            self.cpp_info.defines.append("ZOE_EXPORTS")
        else:
            self.cpp_info.defines.append("ZOE_STATIC")

        # https://github.com/winsoft666/zoe/blob/master/src/CMakeLists.txt#L88
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "crypt32"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
