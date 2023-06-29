from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=1.53.0"


class LibDataChannelConan(ConanFile):
    name = "libdatachannel"
    description = "C/C++ WebRTC network library featuring Data Channels, Media Transport, and WebSockets"
    topics = ("webrtc")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/paullouisageneau/libdatachannel"
    license = "MPL-2.0 license"
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

    def config_options(self):
        pass

    def configure(self):
        pass

    def layout(self):
        pass

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

    def build_requirements(self):
        pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["repo"], destination=self.source_folder, strip_root=True)

        get(self, **self.conan_data["sources"][self.version]["json"], destination=os.path.join(self.source_folder, "deps", "json"), strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["libjuice"], destination=os.path.join(self.source_folder, "deps", "libjuice"), strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["libsrtp"], destination=os.path.join(self.source_folder, "deps", "libsrtp"), strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["plog"], destination=os.path.join(self.source_folder, "deps", "plog"), strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["usrsctp"], destination=os.path.join(self.source_folder, "deps", "usrsctp"), strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
