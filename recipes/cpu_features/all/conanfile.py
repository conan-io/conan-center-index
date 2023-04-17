from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class CpuFeaturesConan(ConanFile):
    name = "cpu_features"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/cpu_features"
    description = "A cross platform C99 library to get cpu features at runtime."
    topics = ("cpu", "features", "cpuid")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.compiler.rm_safe("cppstd")
        self.settings.compiler.rm_safe("libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "0.7.0":
            tc.variables["BUILD_PIC"] = self.options.get_safe("fPIC", True)
        if Version(self.version) >= "0.7.0":
            tc.variables["BUILD_TESTING"] = False
        # TODO: should be handled by CMake helper
        if is_apple_os(self) and self.settings.arch in ["armv8", "armv8_32", "armv8.3"]:
            tc.variables["CMAKE_SYSTEM_PROCESSOR"] = "aarch64"
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CpuFeatures")
        self.cpp_info.set_property("cmake_target_name", "CpuFeatures::cpu_features")

        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["libcpu_features"].libs = ["cpu_features"]
        self.cpp_info.components["libcpu_features"].includedirs = [os.path.join("include", "cpu_features")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libcpu_features"].system_libs = ["dl"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "CpuFeatures"
        self.cpp_info.names["cmake_find_package_multi"] = "CpuFeatures"
        self.cpp_info.components["libcpu_features"].names["cmake_find_package"] = "cpu_features"
        self.cpp_info.components["libcpu_features"].names["cmake_find_package_multi"] = "cpu_features"
        self.cpp_info.components["libcpu_features"].set_property("cmake_target_name", "CpuFeatures::cpu_features")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
