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
    package_type = "library"
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
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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

        self.cpp_info.components["libcpu_features"].libs = ["cpu_features"]
        self.cpp_info.components["libcpu_features"].includedirs = [os.path.join("include", "cpu_features")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libcpu_features"].system_libs = ["dl"]

        if self.settings.os == "Android":
            # FIXME: cpu_features generates CpuFeaturesNdkCompat.cmake too, but CMakeDeps still can not do it
            # See https://github.com/conan-io/conan/pull/18821
            self.cpp_info.components["ndk_compat"].libs = ["ndk_compat"]
            self.cpp_info.components["ndk_compat"].set_property("cmake_file_name", "CpuFeaturesNdkCompat")
            self.cpp_info.components["ndk_compat"].set_property("cmake_target_name", "CpuFeatures::ndk_compat")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
