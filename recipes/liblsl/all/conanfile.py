from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir, replace_in_file, save
import os

required_conan_version = ">=1.54.0"


class LiblslConan(ConanFile):
    name = "liblsl"
    description = "Lab Streaming Layer is a C++ library for multi-modal " \
                  "time-synched data transmission over the local network"
    license = "MIT"
    topics = ("labstreaminglayer", "lsl", "network", "stream", "signal", 
              "transmission")
    homepage = "https://github.com/sccn/liblsl"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def requirements(self):
        self.requires("boost/1.78.0")
        self.requires("pugixml/1.11")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LSL_BUILD_STATIC"] = not self.options.shared
        tc.variables["LSL_BUNDLED_BOOST"] = False
        tc.variables["LSL_BUNDLED_PUGIXML"] = False
        tc.variables["lslgitrevision"] = "v" + self.version
        tc.variables["lslgitbranch"] = "master"
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def _patch_sources(self):
        if not self.options.shared:
            # Do not force PIC
            replace_in_file(
                self,
                os.path.join(self.source_folder, "CMakeLists.txt"),
                "set(CMAKE_POSITION_INDEPENDENT_CODE ON)",
                ""
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        rm(self, "lslver*", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LSL")
        self.cpp_info.set_property("cmake_target_name", "LSL::lsl")
        # TODO: back to global scope in conan v2
        self.cpp_info.components["_liblsl"].libs = ["lsl"]
        self.cpp_info.components["_liblsl"].defines = ["LSLNOAUTOLINK"]
        if not self.options.shared:
            self.cpp_info.components["_liblsl"].defines.append("LIBLSL_STATIC")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_liblsl"].system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["_liblsl"].system_libs = ["iphlpapi", "winmm", "mswsock", "ws2_32"]

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "LSL"
        self.cpp_info.names["cmake_find_package_multi"] = "LSL"
        self.cpp_info.components["_liblsl"].names["cmake_find_package"] = "lsl"
        self.cpp_info.components["_liblsl"].names["cmake_find_package_multi"] = "lsl"
        self.cpp_info.components["_liblsl"].set_property("cmake_target_name", "LSL::lsl")
