from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.microsoft import is_msvc, check_min_vs
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.files import get, copy
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.50.0"


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

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
        }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder,
             self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        if Version(self.version) <= "cci.20211220":
            self.requires("qt/5.15.5")
        else:
            self.requires("qt/6.3.1")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(
                str(self.info.settings.compiler), False)
            if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support."
                )
        qt = self.dependencies["qt"]
        if not qt.options.qtdeclarative:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires option qt:qtdeclarative=True")

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"), keep_path=False)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["runtimeqml"]
