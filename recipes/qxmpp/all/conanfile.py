import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, mkdir, rename, rmdir

required_conan_version = ">=1.53.0"


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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("qt/6.6.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_gstreamer:
            self.requires("gstreamer/1.22.3")
            self.requires("glib/2.78.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["BUILD_DOCUMENTATION"] = "OFF"
        tc.variables["BUILD_TESTS"] = "OFF"
        tc.variables["BUILD_EXAMPLES"] = "OFF"
        tc.variables["WITH_GSTREAMER"] = self.options.with_gstreamer
        tc.variables["BUILD_SHARED"] = self.options.shared
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

        if self.options.shared and self.settings.os == "Windows":
            mkdir(self, os.path.join(self.package_folder, "bin"))
            rename(self,
                os.path.join(self.package_folder, "lib", "qxmpp.dll"),
                os.path.join(self.package_folder, "bin", "qxmpp.dll"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "QXmpp")
        self.cpp_info.set_property("cmake_target_name", "QXmpp::QXmpp")
        self.cpp_info.set_property("pkg_config_name", "qxmpp")
        self.cpp_info.libs = ["qxmpp"]
        self.cpp_info.includedirs.append(os.path.join("include", "qxmpp"))
        self.cpp_info.requires = ["qt::qtCore", "qt::qtNetwork", "qt::qtXml"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "QXmpp"
        self.cpp_info.names["cmake_find_package_multi"] = "QXmpp"
