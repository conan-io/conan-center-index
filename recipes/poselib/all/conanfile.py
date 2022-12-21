from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conans.tools import collect_libs
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import copy, rmdir, get, export_conandata_patches
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
import os

required_conan_version = ">=1.53.0"


class PoseLibConan(ConanFile):
    name = "poselib"
    description = "Minimal solvers for calibrated camera pose estimation"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/vlarsson/PoseLib"
    topics = ("camera pose estimation", "ransac", "multiple view geometry")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "clang": "7",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("eigen/3.4.0")

    def validate(self):
        if self.settings.compiler == "apple-clang":
            raise ConanInvalidConfiguration(f"{self.ref} does not support apple-clang compiler")
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeDeps(self)
        tc.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if is_msvc(self) and self.options.shared:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

        self.cpp_info.libs = collect_libs(self)

        self.cpp_info.set_property("cmake_file_name", "poselib")
        self.cpp_info.set_property("cmake_target_name", "poselib::poselib")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        self.cpp_info.filenames["cmake_find_package"] = "POSELIB"
        self.cpp_info.filenames["cmake_find_package_multi"] = "poselib"
        self.cpp_info.names["cmake_find_package"] = "POSELIB"
        self.cpp_info.names["cmake_find_package_multi"] = "poselib"
