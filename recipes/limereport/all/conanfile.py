from conans import tools
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rm, rmdir
from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.apple import fix_apple_shared_install_name
import os


class LimereportConan(ConanFile):
    name = "limereport"
    description = "Report generator for Qt Framework"
    homepage = "https://poppler.freedesktop.org/"
    topics = ("conan", "limereport", "pdf", "report","qt")
    license = "LGPL-3.0", "GPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zint": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_zint": False,
        "qt:qtquickcontrols": True,
        "qt:qtquickcontrols2": True,
        "qt:qtsvg": True,
        "qt:qttools": True
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC


    def export_sources(self):
        export_conandata_patches(self)

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
        self.build_requires("libpng/1.6.38")
        if self.options.with_zint:
            self.build_requires("zint/2.10.0")

    def requirements(self):
        self.requires("qt/5.15.7")


    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIMEREPORT_STATIC"] = not self.options.shared
        if is_msvc(self):
            tc.variables["WINDOWS_BUILD"] = True
        qt_major = tools.Version(self.deps_cpp_info["qt"].version).major
        if qt_major == 6: 
            tc.variables["USE_QT6"] = True
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()


    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
            
    def package(self):
        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        fix_apple_shared_install_name(self)

    def package_info(self):
        qt_major = tools.Version(self.deps_cpp_info["qt"].version).major
        self.cpp_info.libs = ["limereport-qt{}".format(qt_major)]
        # self.cpp_info.requires = ["qt::qtCore", "qt::qtGui", "qt::qtWidgets", "qt::qtPrintSupport", "qt::qtQml", "qt::qtSvg"]
        # # self.cpp_info.names["cmake_find_package"] = ["limereport-qt{}".format(qt_major)]
        # # self.cpp_info.names["cmake_find_package_multi"] = ["limereport-qt{}".format(qt_major)]

