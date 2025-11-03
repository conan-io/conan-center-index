import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeDeps
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.files import get, replace_in_file, rmdir, copy
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc


class DbusCXX(ConanFile):
    name = "dbus-cxx"
    license = "LGPL-3.0-only", "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://dbus-cxx.github.io"
    description = "DBus-cxx provides an object-oriented interface to DBus"
    topics = "bus", "interprocess", "message"
    package_type = "shared-library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "with_glib": [True, False],
        "with_qt": [True, False],
        "with_uv": [True, False],
    }
    # Default to a relocatable static library with only the default
    # standalone dispatcher
    default_options = {
        "fPIC": True,
        "with_glib": False,
        "with_qt": False,
        "with_uv": False,
    }

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("The recipe only supports Linux.")
        check_min_cppstd(self, 17)
        if (Version(self.version) < "2.6.0" and self.options.get_safe("with_uv")
                and not self.dependencies["libuv"].options.shared):
            raise ConanInvalidConfiguration(f"libuv needs to be shared for "
                                            f"{self.name}/{self.version}: \"libuv/*:shared=True\"")

    def requirements(self):
        self.requires("libsigcpp/3.0.7", transitive_headers=True)
        if self.options.get_safe("with_glib"):
            self.requires("glib/2.81.0", transitive_headers=True)
        if self.options.get_safe("with_uv"):
            self.requires("libuv/[>=1 <2]", transitive_headers=True)
        if self.options.with_qt:
            self.requires("qt/[~5.15]", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        if Version(self.version) < "2.6.0":
            # Version 2.5.2 or earlier
            replace_in_file(self, os.path.join(self.source_folder, "dbus-cxx-uv", "CMakeLists.txt"),
                            "pkg_search_module( LIBUV REQUIRED libuv )",
                            "pkg_search_module( LIBUV IMPORTED_TARGET libuv )")
            replace_in_file(self, os.path.join(self.source_folder, "dbus-cxx-uv", "CMakeLists.txt"),
                            "target_link_libraries( dbus-cxx-uv PUBLIC ${LIBUV_LIBRARIES} )",
                            "target_link_libraries( dbus-cxx-uv PUBLIC PkgConfig::LIBUV )")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["ENABLE_CODE_COVERAGE_REPORT"] = False
        tc.cache_variables["ENABLE_EXAMPLES"] = False
        tc.cache_variables["ENABLE_TOOLS"] = False  # note: requires expat lib
        tc.cache_variables["BUILD_SITE"] = False
        tc.cache_variables["ENABLE_GLIB_SUPPORT"] = self.options.with_glib
        tc.cache_variables["ENABLE_QT_SUPPORT"] = self.options.with_qt
        tc.cache_variables["ENABLE_UV_SUPPORT"] = self.options.with_uv
        if (Version(self.version) >= "2.6.0" and self.options.with_uv
                and not self.dependencies["libuv"].options.shared):
            tc.cache_variables["UV_STATIC"] = True
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # remove useless folders
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # dbus-cxx
        self.cpp_info.components["dbus-cxx"].libs = ["dbus-cxx"]
        self.cpp_info.components["dbus-cxx"].requires = ["libsigcpp::sigc++"]
        self.cpp_info.components["dbus-cxx"].includedirs = ['include/dbus-cxx-2.0']
        self.cpp_info.components["dbus-cxx"].set_property("cmake_target_name", "dbus-cxx")
        self.cpp_info.components["dbus-cxx"].set_property("pkg_config_name", "dbus-cxx-2.0")
        # dbus-cxx-glib
        if self.options.with_glib:
            self.cpp_info.components["dbus-cxx-glib"].libs = ["dbus-cxx-glib"]
            self.cpp_info.components["dbus-cxx-glib"].requires = ["dbus-cxx", "libsigcpp::sigc++", "glib::glib-2.0"]
            self.cpp_info.components["dbus-cxx-glib"].includedirs = ['include/dbus-cxx-glib-2.0']
            self.cpp_info.components["dbus-cxx-glib"].set_property("cmake_target_name", "dbus-cxx-glib")
            self.cpp_info.components["dbus-cxx-glib"].set_property("pkg_config_name", "dbus-cxx-glib-2.0")
        # dbus-cxx-qt
        if self.options.with_qt:
            self.cpp_info.components["dbus-cxx-qt"].libs = ["dbus-cxx-qt"]
            self.cpp_info.components["dbus-cxx-qt"].requires = ["dbus-cxx", "libsigcpp::sigc++", "qt::qtCore"]
            self.cpp_info.components["dbus-cxx-qt"].includedirs = ['include/dbus-cxx-qt-2.0']
            self.cpp_info.components["dbus-cxx-qt"].set_property("cmake_target_name", "dbus-cxx-qt")
            self.cpp_info.components["dbus-cxx-qt"].set_property("pkg_config_name", "dbus-cxx-qt-2.0")
        # dbus-cxx-uv
        if self.options.get_safe("with_uv"):
            self.cpp_info.components["dbus-cxx-uv"].libs = ["dbus-cxx-uv"]
            self.cpp_info.components["dbus-cxx-uv"].requires = ["dbus-cxx", "libsigcpp::sigc++", "libuv::libuv"]
            self.cpp_info.components["dbus-cxx-uv"].includedirs = ['include/dbus-cxx-uv-2.0']
            self.cpp_info.components["dbus-cxx-uv"].set_property("cmake_target_name", "dbus-cxx-uv")
            self.cpp_info.components["dbus-cxx-uv"].set_property("pkg_config_name", "dbus-cxx-uv-2.0")
