import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.0.9"


class ResiprocateConan(ConanFile):
    name = "resiprocate"
    description = (
        "The project is dedicated to maintaining a complete, correct, "
        "and commercially usable implementation of SIP and a few related protocols."
    )
    license = "VSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/resiprocate/resiprocate/wiki/"
    topics = ("sip", "voip", "communication", "signaling")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cares": [True, False],
        "with_ssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_cares": True,
        "with_ssl": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_cares:
            self.requires("c-ares/[>=1.27 <2]")
        if self.options.with_ssl:
            self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        check_min_cppstd(self, 11)
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21 <4]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_DSO_PLUGINS"] = False
        tc.variables["BUILD_QPID_PROTON"] = False
        tc.variables["BUILD_RECON"] = False
        tc.variables["BUILD_REFLOW"] = False
        tc.variables["BUILD_REND"] = False
        tc.variables["BUILD_REPRO"] = False
        tc.variables["BUILD_RETURN"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_TFM"] = False
        tc.variables["ENABLE_LOG_REPOSITORY_DETAILS"] = False
        tc.variables["REGENERATE_MEDIA_SAMPLES"] = False
        tc.variables["RESIP_ASSERT_SYSLOG"] = False
        tc.variables["USE_CONTRIB"] = False
        tc.variables["USE_DTLS"] = self.options.with_ssl
        tc.variables["USE_KURENTO"] = False
        tc.variables["USE_MAXMIND_GEOIP"] = False
        tc.variables["USE_NUGET"] = False
        tc.variables["USE_POPT"] = False
        tc.variables["VERSIONED_SONAME"] = False
        tc.variables["WITH_C_ARES"] = self.options.with_cares
        tc.variables["WITH_SSL"] = self.options.with_ssl
        if self.settings.os in ["Linux"]:
            tc.preprocessor_definitions["RESIP_RANDOM_THREAD_LOCAL"] = True
        if cross_building(self):
            tc.cache_variables["HAVE_CLOCK_GETTIME_MONOTONIC"] = not self.settings.os in ["Windows"]
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        resiprocate_lib = "resiprocate" if self.settings.os == "Windows" else "resip"
        self.cpp_info.libs = [resiprocate_lib, "rutil", "dum"]
        if not self.options.with_cares:
            self.cpp_info.libs.append("resipares")
        if is_apple_os(self):
            self.cpp_info.frameworks.extend(["CoreFoundation", "CoreServices", "Security"])
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        elif self.settings.os in ["Windows"]:
            self.cpp_info.system_libs.extend(["winmm", "ws2_32"])
