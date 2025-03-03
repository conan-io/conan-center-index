import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy
from conan.tools.scm import Version

required_conan_version = ">=2.0.9"


class RuntimeQml(ConanFile):
    name = "runtimeqml"
    homepage = "https://github.com/GIPdA/runtimeqml"
    description = "Enables hot-reloading qml files"
    topics = ("qt", "hot-reload", "qml", "gui")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=os.path.join(self.export_sources_folder, "src"))

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _qt_options(self):
        return {
            "qtdeclarative": True,
            "qtshadertools": True,
        }

    def requirements(self):
        qt_version = "[>=6.6 <7]" if Version(self.version) >= "cci.20220923" else "[~5.15]"
        self.requires(f"qt/{qt_version}", transitive_headers=True, transitive_libs=True, options=self._qt_options)

    def validate(self):
        check_min_cppstd(self, 17)
        qt_opt = self.dependencies["qt"].options
        if not (qt_opt.qtdeclarative and qt_opt.qtshadertools):
            raise ConanInvalidConfiguration(f"{self.ref} requires options qt:qtdeclarative=True and qt:qtshadertools=True")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.27 <4]")
        self.tool_requires("qt/<host_version>", options=self._qt_options)

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["runtimeqml"]
        self.cpp_info.requires = ["qt::qtCore", "qt::qtQuick", "qt::qtWidgets"]
