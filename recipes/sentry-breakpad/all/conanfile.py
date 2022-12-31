from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os

required_conan_version = ">=1.53.0"


class SentryBreakpadConan(ConanFile):
    name = "sentry-breakpad"
    description = "Client component that implements a crash-reporting system."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/getsentry/breakpad"
    license = "Apache-2.0"
    topics = ("conan", "breakpad", "error-reporting", "crash-reporting")
    provides = "breakpad"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ("FreeBSD", "Linux"):
            self.requires("linux-syscall-support/cci.20200813")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        if Version(self.version) <= "0.4.1":
            if self.settings.os == "Android" or is_apple_os(self):
                raise ConanInvalidConfiguration("Versions <=0.4.1 do not support Apple or Android")
        if Version(self.version) <= "0.2.6":
            if self.settings.os == "Windows":
                raise ConanInvalidConfiguration("Versions <=0.2.6 do not support Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder="external")
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=os.path.join(self.source_folder, "external", "breakpad"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "breakpad-client"
        self.cpp_info.libs = ["breakpad_client"]
        self.cpp_info.includedirs.append(os.path.join("include", "breakpad"))
        if is_apple_os(self):
            self.cpp_info.frameworks.append("CoreFoundation")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
