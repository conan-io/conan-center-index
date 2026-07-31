import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.gnu import PkgConfigDeps

required_conan_version = ">=2.1"


class SdbusCppConan(ConanFile):
    name = "sdbus-cpp"
    license = "LicenseRef-LGPL-2.1-or-later-WITH-sdbus-cpp-LGPL-exception-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Kistler-Group/sdbus-cpp"
    description = "High-level C++ D-Bus library for Linux designed" \
                  " to provide easy-to-use yet powerful API in modern C++"
    topics = ("dbus", "sd-bus", "sdbus-c++")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_code_gen": [True, False],
        "with_sdbus": ["systemd", "basu"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_code_gen": False,
        "with_sdbus": "systemd",
    }

    @property
    def _with_sdbus(self):
        return ("basu" if self.settings.os == "FreeBSD"
                else self.options.get_safe("with_sdbus", "systemd"))

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.with_sdbus

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self._with_sdbus == "systemd":
            self.requires("libsystemd/255.2")
        elif self._with_sdbus == "basu":
            self.requires("basu/0.2.1")
        if self.options.with_code_gen:
            # Trick: always force transitive_libs=False, in order to not propagate expat lib
            # transitively even when sdbus-cpp is static, since expat is a dependency of the executable, not the lib
            self.requires("expat/[>=2.6.2 <3]", transitive_libs=False)

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration(
                f"{self.ref} does not support {self.settings.os}")

        check_min_cppstd(self, 20)

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD 20)",
                        "")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SDBUSCPP_BUILD_CODEGEN"] = self.options.with_code_gen
        tc.variables["BUILD_DOC"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_LIBSYSTEMD"] = False
        tc.variables["SDBUSCPP_BUILD_DOCS"] = False
        tc.variables["SDBUSCPP_SDBUS_LIB"] = self._with_sdbus
        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

        if self.options.with_code_gen:
            deps = CMakeDeps(self)
            deps.set_property("expat", "cmake_file_name", "EXPAT")
            deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        copy(self, "COPYING*", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sdbus-c++")
        self.cpp_info.set_property("cmake_target_name", "SDBusCpp::sdbus-c++")
        self.cpp_info.set_property("pkg_config_name", "sdbus-c++")
        self.cpp_info.components["sdbus-c++"].libs = ["sdbus-c++"]
        self.cpp_info.components["sdbus-c++"].system_libs = ["pthread", "m"]

        self.cpp_info.components["sdbus-c++"].set_property(
            "cmake_target_name", "SDBusCpp::sdbus-c++")
        self.cpp_info.components["sdbus-c++"].set_property(
            "pkg_config_name", "sdbus-c++")
        if self._with_sdbus == "systemd":
            self.cpp_info.components["sdbus-c++"].requires.append(
                "libsystemd::libsystemd")
        elif self._with_sdbus == "basu":
            self.cpp_info.components["sdbus-c++"].requires.append(
                "basu::basu")
        if self.options.with_code_gen:
            # Not a dependency of the lib, only of executable, but there is no way to modelize this
            # with conan
            self.cpp_info.components["sdbus-c++"].requires.append("expat::expat")
