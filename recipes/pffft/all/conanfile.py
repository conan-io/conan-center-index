from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, load, save, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class PffftConan(ConanFile):
    name = "pffft"
    description = "PFFFT, a pretty fast Fourier Transform."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/marton78/pffft"
    topics = ("fft", "pffft")
    license = "BSD-like (FFTPACK license)"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_simd": [True, False],
        # v1.0+ options
        "with_float": [True, False],
        "with_double": [True, False],
        "with_pffastconv": [True, False],
        "with_pfdsp": [True, False],
        "with_simd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_simd": False,
        # v1.0+ defaults
        "with_float": True,
        "with_double": True,
        "with_pffastconv": False,
        "with_pfdsp": False,
        "with_simd": True,
    }

    exports_sources = "CMakeLists.txt"

    @property
    def _is_legacy(self):
        return Version(self.version) < "1.0"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self._is_legacy:
            del self.options.with_float
            del self.options.with_double
            del self.options.with_pffastconv
            del self.options.with_pfdsp
            del self.options.with_simd
        else:
            del self.options.disable_simd

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self._is_legacy:
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")
        elif not self.options.get_safe("with_pfdsp"):
            # Pure C library when pfdsp is not built
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")

    def validate(self):
        if not self._is_legacy:
            if not self.options.with_float and not self.options.with_double:
                raise ConanInvalidConfiguration(
                    f"{self.ref}: at least one of 'with_float' or 'with_double' must be enabled"
                )
            if self.options.with_pffastconv and not self.options.with_float:
                raise ConanInvalidConfiguration(
                    f"{self.ref}: 'with_pffastconv' requires 'with_float' to be enabled"
                )
            if self.options.with_pfdsp and not self.options.with_float:
                raise ConanInvalidConfiguration(
                    f"{self.ref}: 'with_pfdsp' requires 'with_float' to be enabled"
                )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self._is_legacy:
            tc.variables["PFFFT_SRC_DIR"] = self.source_folder.replace("\\", "/")
            tc.variables["DISABLE_SIMD"] = self.options.disable_simd
        else:
            tc.variables["PFFFT_USE_TYPE_FLOAT"] = self.options.with_float
            tc.variables["PFFFT_USE_TYPE_DOUBLE"] = self.options.with_double
            tc.variables["PFFFT_USE_SIMD"] = self.options.with_simd
            tc.variables["INSTALL_PFFFT"] = True
            tc.variables["INSTALL_PFFASTCONV"] = self.options.with_pffastconv
            tc.variables["INSTALL_PFDSP"] = self.options.with_pfdsp
            tc.variables["PFFFT_BUILD_TESTS"] = False
            tc.variables["PFFFT_BUILD_BENCHMARKS"] = False
            tc.variables["PFFFT_BUILD_EXAMPLES"] = False
        tc.generate()
        if not self._is_legacy:
            deps = CMakeDeps(self)
            deps.generate()

    def build(self):
        cmake = CMake(self)
        if self._is_legacy:
            cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        else:
            cmake.configure()
        cmake.build()

    def package(self):
        if self._is_legacy:
            header = load(self, os.path.join(self.source_folder, "pffft.h"))
            license_content = header[: header.find("*/", 1)]
            save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_content)
        else:
            copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        if self._is_legacy:
            self.cpp_info.libs = ["pffft"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("m")
        else:
            self.cpp_info.set_property("cmake_file_name", "pffft")

            self.cpp_info.components["pffft"].set_property(
                "cmake_target_name", "PFFFT::PFFFT"
            )
            self.cpp_info.components["pffft"].libs = ["pffft"]
            # Expose both include/ (for #include <pffft/pffft.h>) and
            # include/pffft/ (for #include <pffft.h> legacy compat)
            self.cpp_info.components["pffft"].includedirs = [
                "include", os.path.join("include", "pffft")
            ]
            if self.settings.os != "Windows":
                self.cpp_info.components["pffft"].system_libs.append("m")

            if self.options.with_pffastconv:
                self.cpp_info.components["pffastconv"].set_property(
                    "cmake_target_name", "PFFFT::PFFASTCONV"
                )
                self.cpp_info.components["pffastconv"].libs = ["pffastconv"]
                self.cpp_info.components["pffastconv"].requires = ["pffft"]
                if self.settings.os != "Windows":
                    self.cpp_info.components["pffastconv"].system_libs.append("m")

            if self.options.with_pfdsp:
                self.cpp_info.components["pfdsp"].set_property(
                    "cmake_target_name", "PFFFT::PFDSP"
                )
                self.cpp_info.components["pfdsp"].libs = ["pfdsp"]
                if self.settings.os != "Windows":
                    self.cpp_info.components["pfdsp"].system_libs.append("m")
