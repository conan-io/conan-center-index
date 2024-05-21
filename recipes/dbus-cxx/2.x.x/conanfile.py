from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.gnu import PkgConfigDeps
from conan.tools.files import get
from conan.tools.scm import Version

class DbusCXX(ConanFile):
    name = "dbus-cxx"
    license = "LGPL-3.0-only", "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://dbus-cxx.github.io"
    description = "DBus-cxx provides an object-oriented interface to DBus"
    topics = "bus", "interprocess", "message"
    package_type = "static-library"
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "fPIC": [True, False],
        "with_glib": [True, False],
        "with_qt": [True, False],
        "with_uv": [True, False],
    }

    @property
    def _min_cppstd(self):
        return 17

    # Default to a relocatable static library with only the default
    # standalone dispatcher
    default_options = {
        "fPIC": True,
        "with_glib": False,
        "with_qt": False,
        "with_uv": False,
   }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "2.5.0":
            del self.options.with_uv

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def requirements(self):
        self.requires("libsigcpp/3.0.7", transitive_headers=True)
        self.requires("expat/[>=2.6.2 <3]")

        if self.options.get_safe("with_uv"):
            self.requires("libuv/[>=1.0 <2.0]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ENABLE_GLIB_SUPPORT"] = self.options.with_glib
        tc.cache_variables["ENABLE_QT_SUPPORT"] = self.options.with_qt
        if Version(self.version) >= "2.5.0":
            tc.cache_variables["ENABLE_UV_SUPPORT"] = self.options.with_uv
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        if self.options.with_glib:
            self.cpp_info.libs.append("dbus-cxx-glib")
        if self.options.with_qt:
            self.cpp_info.libs.append("dbus-cxx-qt")
        if self.options.get_safe("with_uv"):
            self.cpp_info.libs.append("dbus-cxx-uv")

        self.cpp_info.libs.append("dbus-cxx")
        self.cpp_info.includedirs = ['include/dbus-cxx-2.0']
