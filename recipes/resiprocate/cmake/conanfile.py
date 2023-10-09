import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps

required_conan_version = ">=1.53.0"


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
        "with_ssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": True,
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
        self.requires("c-ares/1.19.1")
        if self.options.with_ssl:
            self.requires("openssl/[>=1.1 <4]")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_DSO_PLUGINS"] = False
        tc.variables["BUILD_QPID_PROTON"] = False
        tc.variables["BUILD_REPRO"] = False
        tc.variables["BUILD_RETURN"] = False
        tc.variables["ENABLE_LOG_REPOSITORY_DETAILS"] = False
        tc.variables["REGENERATE_MEDIA_SAMPLES"] = False
        tc.variables["RESIP_ASSERT_SYSLOG"] = False
        tc.variables["USE_CONTRIB"] = False
        tc.variables["USE_DTLS"] = self.options.with_ssl
        tc.variables["USE_NUGET"] = False
        tc.variables["WITH_C_ARES"] = True
        tc.variables["WITH_SSL"] = self.options.with_ssl
        if self.settings.os in ["Linux"]:
            tc.preprocessor_definitions["RESIP_RANDOM_THREAD_LOCAL"] = True
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

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
        self.cpp_info.libs = ["resip", "rutil", "dum"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
