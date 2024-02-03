from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get
from conan.tools.build import check_min_cppstd
from conan import ConanFile
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
    package_type = "library"
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

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "8",
            "apple-clang": "9.1",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.requires("libpng/1.6.42")
        if self.options.with_zint:
            self.tool_requires("zint/2.10.0")

    def requirements(self):
        self.requires("qt/6.4.2")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )    
        if Version(self.dependencies["qt"].ref.version) < "6.0.0":
            if not (self.dependencies["qt"].options.qtquickcontrols and self.dependencies["qt"].options.qtquickcontrols2):
                raise ConanInvalidConfiguration(f"{self.ref} requires qt:quickcontrols=True and qt:quickcontrols2=True")
            elif not (self.dependencies["qt"].options.qtdeclarative):
                raise ConanInvalidConfiguration(f"{self.ref} requires qt:qtdeclarative=True")
        if not (self.dependencies["qt"].options.qtsvg and self.dependencies["qt"].options.qttools):
            raise ConanInvalidConfiguration(f"{self.ref} requires qt:qtsvg=True and qt:qttools=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["LIMEREPORT_STATIC"] = not self.options.shared
        if is_msvc(self):
            tc.variables["WINDOWS_BUILD"] = True
        qt_major = Version(self.dependencies["qt"].ref.version).major
        if qt_major == 6: 
            tc.cache_variables["USE_QT6"] = True
        tc.cache_variables["ENABLE_ZINT"] = self.options.with_zint
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def configure(self):
        self.options.rm_safe("fPIC")

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
        qt_major = Version(self.dependencies["qt"].ref.version).major
        self.cpp_info.libs = ["limereport-qt{}".format(qt_major)]
