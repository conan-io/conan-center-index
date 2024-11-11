from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rm, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=2.0.9"


class SpixConan(ConanFile):
    name = "spix"
    description = "UI test automation library for QtQuick/QML Apps"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/faaxm/spix"
    topics = ("automation", "qt", "qml", "qt-quick", "qtquick", "automated-testing", "qt-qml", "qml-applications")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    @property
    def _minimum_cpp_standard(self):
        return 14 if self.version == "0.4" else 17

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _qt_options(self):
        return {
            "qtdeclarative": True,
            "qtshadertools": True,
        }

    def requirements(self):
        self.requires("anyrpc/1.0.2")
        # Uses #include <QObject> in the Spix/QtQmlBot.h public header
        self.requires("qt/[>=6.6 <7]", transitive_headers=True, transitive_libs=True, options=self._qt_options)

    def validate(self):
        check_min_cppstd(self, self._minimum_cpp_standard)
        qt = self.dependencies["qt"]
        if qt.ref.version.major == 6 and not qt.options.qtshadertools:
            raise ConanInvalidConfiguration(f"{self.ref} requires qt:qtshadertools to get the Quick module")
        if not (qt.options.gui and qt.options.qtdeclarative):
            raise ConanInvalidConfiguration(f"{self.ref} requires qt:gui and qt:qtdeclarative to get the Quick module")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.27 <4]")
        self.tool_requires("qt/<host_version>", options=self._qt_options)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        rmdir(self, os.path.join(self.source_folder, "cmake", "modules"))
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD ", "# set(CMAKE_CXX_STANDARD ")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SPIX_BUILD_EXAMPLES"] = False
        tc.cache_variables["SPIX_BUILD_TESTS"] = False
        tc.cache_variables["SPIX_QT_MAJOR"] = str(self.dependencies["qt"].ref.version.major)
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("anyrpc", "cmake_file_name", "AnyRPC")
        deps.set_property("anyrpc", "cmake_target_name", "AnyRPC::anyrpc")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["Spix"]
        self.cpp_info.set_property("cmake_file_name", "Spix")
        self.cpp_info.set_property("cmake_target_name", "Spix::Spix")
