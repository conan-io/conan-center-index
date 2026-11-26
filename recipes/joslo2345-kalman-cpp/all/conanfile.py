from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0"


class Joslo2345KalmanCppConan(ConanFile):
    name = "joslo2345-kalman-cpp"
    description = (
        "Header-only C++20 Kalman filters (KF, square-root KF, EKF with automatic Jacobians, UKF, "
        "square-root UKF, error-state on SO(3)), RTS smoother and asynchronous sensor fusion"
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/joslo2345/kalman-cpp"
    topics = ("kalman-filter", "state-estimation", "sensor-fusion", "eigen", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        # C++20 concepts, requires-expressions and <numbers>.
        return {
            "gcc": "11",
            "clang": "14",
            "apple-clang": "14",
            "msvc": "193",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        # Same names as the project's own CMake package.
        self.cpp_info.set_property("cmake_file_name", "kalman")
        self.cpp_info.set_property("cmake_target_name", "kalman::kalman")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.requires = ["eigen::eigen"]
