from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import copy, get
from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conan.tools.apple import fix_apple_shared_install_name
from conan.errors import ConanInvalidConfiguration
import os


class LimereportConan(ConanFile):
    name = "limereport"
    description = "Report generator for Qt Framework"
    homepage = "https://poppler.freedesktop.org/"
    topics = ("limereport", "pdf", "report","qt")
    license = "LGPL-3.0", "GPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zint": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zint": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "8",
            "clang": "8",
            "apple-clang": "8"
        }

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.requires("libpng/[>=1.6 <1.7]")
        if self.options.with_zint:
            self.build_requires("zint/2.10.0")

    def requirements(self):
        self.requires("qt/6.4.2")

    def validate(self):
        if Version(self.dependencies["qt"].ref.version) < "6.0.0":
            if not (self.dependencies["qt"].options.qtquickcontrols and self.dependencies["qt"].options.qtquickcontrols2):
                raise ConanInvalidConfiguration(f"{self.ref} requires qt quickcontrols and quickcontrols2")
        if not (self.dependencies["qt"].options.qtsvg and self.dependencies["qt"].options.qttools):
            raise ConanInvalidConfiguration(f"{self.ref} requires qt svg and tools")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["LIMEREPORT_STATIC"] = not self.options.shared
        if is_msvc(self):
            tc.variables["WINDOWS_BUILD"] = True
        qt_major = Version(self.deps_cpp_info["qt"].version).major
        if qt_major == 6: 
            tc.cache_variables["USE_QT6"] = True
        tc.cache_variables["ENABLE_ZINT"] = self.options.with_zint
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()


    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
            
    def package(self):
        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        fix_apple_shared_install_name(self)

    def package_info(self):
        qt_major = Version(self.deps_cpp_info["qt"].version).major
        self.cpp_info.libs = ["limereport-qt{}".format(qt_major)]
