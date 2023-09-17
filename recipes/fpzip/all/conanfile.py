from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"

class FpzipConan(ConanFile):
    name = "fpzip"
    description = "Lossless compressor of multidimensional floating-point arrays"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://fpzip.llnl.gov/"
    topics = ("compression", "lossless", "floating-point")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_fp": ["fast", "safe", "emul", "int"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_fp": "fast",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _fp_name_table(self):
        return  {
            "fast": "FPZIP_FP_FAST",
            "safe": "FPZIP_FP_SAFE",
            "emul": "FPZIP_FP_EMUL",
            "int": "FPZIP_FP_INT",
        }

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FPZIP_FP"] = self._fp_name_table.get(str(self.options.with_fp), "FP_ZIP_FAST")
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["fpzip"]
        self.cpp_info.defines.append("FPZIP_FP={}".format(self._fp_name_table.get(str(self.options.with_fp), "FP_ZIP_FAST")))
        if self.options.shared:
            self.cpp_info.defines.append("FPZIP_SHARED_LIBS")
        if self.settings.compiler in ["gcc", "clang", "apple-clang"]:
            self.cpp_info.system_libs += ["stdc++"]
