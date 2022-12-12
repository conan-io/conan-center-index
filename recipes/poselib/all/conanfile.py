from conan import ConanFile
from conan.tools.files import copy, rmdir, get
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("eigen/3.4.0")

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
        self.cpp_info.libs = ["PoseLib"]

        self.cpp_info.set_property("cmake_file_name", "poselib")
        self.cpp_info.set_property("cmake_target_name", "poselib::poselib")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        self.cpp_info.filenames["cmake_find_package"] = "POSELIB"
        self.cpp_info.filenames["cmake_find_package_multi"] = "poselib"
        self.cpp_info.names["cmake_find_package"] = "POSELIB"
        self.cpp_info.names["cmake_find_package_multi"] = "poselib"
