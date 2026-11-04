import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, rename, mkdir
from conan.tools.microsoft import is_msvc
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.scm import Version

required_conan_version = ">=1.60.0 <2 || >=2.0.5"


class QxmppConan(ConanFile):
    name = "qxmpp"
    description = ("Cross-platform C++ XMPP client and server library. "
                   "It is written in C++ and uses Qt framework.")
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/qxmpp-project/qxmpp"
    topics = ("qt", "qt6", "xmpp", "xmpp-library", "xmpp-server", "xmpp-client")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_gstreamer": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_gstreamer": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10",
            "Visual Studio": "17",
            "msvc": "192",
            "clang": "8",
            "apple-clang": "13",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("qt/[>=5.15 <7]", transitive_headers=True, transitive_libs=True)
        if self.options.with_gstreamer:
            self.requires("gstreamer/1.22.6")
            self.requires("glib/2.78.3")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def build_requirements(self):
        self.tool_requires("qt/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()
        venv = VirtualRunEnv(self)
        venv.generate(scope="build")
        tc = CMakeToolchain(self)
        tc.variables["BUILD_DOCUMENTATION"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["WITH_GSTREAMER"] = self.options.with_gstreamer
        tc.variables["BUILD_SHARED"] = self.options.get_safe("shared")
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.LGPL", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if is_msvc(self) and self.options.shared:
            mkdir(self, os.path.join(self.package_folder, "bin"))
            rename(self, os.path.join(self.package_folder, "lib", "qxmpp.dll"), os.path.join(self.package_folder, "bin", "qxmpp.dll"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "QXmpp")
        self.cpp_info.set_property("cmake_target_name", "QXmpp::QXmpp")
        self.cpp_info.set_property("pkg_config_name", "qxmpp")
        self.cpp_info.libs = ["qxmpp"]
        self.cpp_info.includedirs.append(os.path.join("include", "qxmpp"))
        self.cpp_info.requires = ["qt::qtCore", "qt::qtNetwork", "qt::qtXml"]
        if self.options.with_gstreamer:
            self.cpp_info.requires.extend(["gstreamer::gstreamer", "glib::glib"])
