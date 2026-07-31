import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2.1"


class SpixConan(ConanFile):
    name = "spix"
    description = "UI test automation library for QtQuick/QML Apps"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/faaxm/spix"
    topics = ("automation", "qt", "qml", "qt-quick", "qt5", "qtquick",
              "automated-testing", "qt-qml", "qml-applications")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("anyrpc/1.0.2")
        self.requires("qt/[>=6.6.1 <7]", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 17)

        qt_dep = self.dependencies["qt"]
        if Version(qt_dep.ref.version).major == 6 and not qt_dep.options.qtshadertools:
            raise ConanInvalidConfiguration("Requires qt:qtshadertools to get the Quick module")
        if not (qt_dep.options.gui and qt_dep.options.qtdeclarative):
            raise ConanInvalidConfiguration("Requires qt:gui and qt:qtdeclarative to get the Quick module")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        rmdir(self, os.path.join(self.source_folder, "cmake", "modules"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SPIX_BUILD_EXAMPLES"] = False
        tc.cache_variables["SPIX_BUILD_TESTS"] = False
        tc.cache_variables["SPIX_QT_MAJOR"] = Version(self.dependencies["qt"].ref.version).major
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("anyrpc", "cmake_file_name", "AnyRPC")
        deps.set_property("anyrpc", "cmake_target_name", "AnyRPC::anyrpc")
        deps.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Spix")
        self.cpp_info.set_property("cmake_target_name", "Spix::Spix")

        self.cpp_info.components["core"].libs = ["SpixCore"]
        self.cpp_info.components["core"].set_property("cmake_target_name", "Spix::Core")
        self.cpp_info.components["core"].requires = [
            "qt::qtCore",
            "anyrpc::anyrpc",
        ]

        self.cpp_info.components["qtquick"].libs = ["SpixQtQuick"]
        self.cpp_info.components["qtquick"].set_property("cmake_target_name", "Spix::QtQuick")
        self.cpp_info.components["qtquick"].requires = [
            "qt::qtQuick",
            "qt::qtGui",
            "qt::qtOpenGL"
        ]
        if self.settings.os == "Macos":
            self.cpp_info.components["qtquick"].requires.append("qt::QCocoaIntegrationPlugin")
