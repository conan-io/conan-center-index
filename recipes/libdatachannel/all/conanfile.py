import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import copy, get, rm, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc
from conan.tools.apple import fix_apple_shared_install_name

required_conan_version = ">=2.1"

class libdatachannelConan(ConanFile):
    name = "libdatachannel"
    description = "C/C++ WebRTC network library featuring Data Channels, Media Transport, and WebSockets."
    license = "MPL-2.0"
    topics = ("webrtc")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/paullouisageneau/libdatachannel"
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_websocket": [True, False],
        "with_nice": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_websocket": True,
        "with_nice": False
    }

    implements = ["auto_shared_fpic"]

    def requirements(self):
        self.requires("openssl/[>=1.1]")
        self.requires("plog/1.1.10")
        self.requires("usrsctp/0.9.5.0")
        self.requires("libsrtp/2.6.0")
        self.requires("nlohmann_json/3.11.3")        
        if self.options.with_nice:
            self.requires("libnice/0.1.21")
        else:
            self.requires("libjuice/1.5.7")

    def validate(self):
        check_min_cppstd(self, 17)
        if self.settings.os == "Windows":
            # TODO: fix windows support
            raise ConanInvalidConfiguration("Does not support Windows yet")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def export_sources(self):
        export_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_SYSTEM_SRTP"] = True
        
        tc.variables["USE_SYSTEM_USRSCTP"] = True
        tc.variables["USE_SYSTEM_PLOG"] = True
        tc.variables["USE_SYSTEM_JSON"] = True
        tc.variables["NO_EXAMPLES"] = True
        tc.variables["NO_TESTS"] = True
        tc.variables["NO_WEBSOCKET"] = not self.options.with_websocket
        tc.variables["USE_NICE"] = self.options.with_nice
        tc.variables["USE_SYSTEM_JUICE"] = not self.options.with_nice
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        fix_apple_shared_install_name(self)

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        suffix = ""
        if is_msvc(self) and self.settings.build_type == "Debug":
            suffix = "d"
        self.cpp_info.libs = ["datachannel" + suffix]
        self.cpp_info.set_property("cmake_file_name", "LibDataChannel")
        self.cpp_info.set_property("cmake_target_name", "LibDataChannel::LibDataChannel")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")

        if is_msvc(self):
            self.cpp_info.cxxflags.append("/bigobj")
