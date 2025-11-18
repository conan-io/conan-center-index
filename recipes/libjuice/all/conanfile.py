import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.apple import fix_apple_shared_install_name

required_conan_version = ">=2.1"

class libjuiceConan(ConanFile):
    name = "libjuice"
    description = "JUICE is a UDP Interactive Connectivity Establishment library."
    license = "MPL-2.0"
    topics = ("webrtc", "ice")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/paullouisageneau/libjuice"
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NO_TESTS"] = True
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
        self.cpp_info.libs = ["juice" + suffix]
        self.cpp_info.set_property("cmake_file_name", "LibJuice")
        if self.options.shared:
            self.cpp_info.set_property("cmake_target_name", "LibJuice::LibJuice")
        else:
            self.cpp_info.set_property("cmake_target_name", "LibJuice::LibJuiceStatic")
            self.cpp_info.defines.append("JUICE_STATIC")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "bcrypt"])

        if is_msvc(self):
            self.cpp_info.cxxflags.append("/bigobj")
