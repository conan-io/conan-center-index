from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class OpenSubdivConan(ConanFile):
    name = "opensubdiv"
    license = "LicenseRef-LICENSE.txt"
    homepage = "https://github.com/PixarAnimationStudios/OpenSubdiv"
    url = "https://github.com/conan-io/conan-center-index"
    description = "An Open-Source subdivision surface library"
    topics = ("cgi", "vfx", "animation", "subdivision surface")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tbb": [True, False],
        "with_opengl": [True, False],
        "with_omp": [True, False],
        "with_cuda": [True, False],
        "with_clew": [True, False],
        "with_opencl": [True, False],
        "with_dx": [True, False],
        "with_metal": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tbb": False,
        "with_opengl": False,
        "with_omp": False,
        "with_cuda": False,
        "with_clew": False,
        "with_opencl": False,
        "with_dx": False,
        "with_metal": False,
    }

    short_paths = True

    @property
    def _min_cppstd(self):
        if self.options.get_safe("with_metal"):
            return "14"
        return "11"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "5",
            "clang": "11",
            "apple-clang": "11.0",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.with_dx
        if self.settings.os != "Macos":
            del self.options.with_metal

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_tbb:
            self.requires("onetbb/2021.8.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if min_version and Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.options.shared and self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} shared not supported on Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _osd_gpu_enabled(self):
        return any(
            [
                self.options.with_opengl,
                self.options.with_opencl,
                self.options.with_cuda,
                self.options.get_safe("with_dx"),
                self.options.get_safe("with_metal"),
            ]
        )

    def generate(self):
        tc = CMakeToolchain(self)
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        tc.variables["NO_TBB"] = not self.options.with_tbb
        tc.variables["NO_OPENGL"] = not self.options.with_opengl
        tc.variables["BUILD_SHARED_LIBS"] = self.options.get_safe("shared")
        tc.variables["NO_OMP"] = not self.options.with_omp
        tc.variables["NO_CUDA"] = not self.options.with_cuda
        tc.variables["NO_DX"] = not self.options.get_safe("with_dx")
        tc.variables["NO_METAL"] = not self.options.get_safe("with_metal")
        tc.variables["NO_CLEW"] = not self.options.with_clew
        tc.variables["NO_OPENCL"] = not self.options.with_opencl
        tc.variables["NO_PTEX"] = True  # Note: PTEX is for examples only, but we skip them..
        tc.variables["NO_DOC"] = True
        tc.variables["NO_EXAMPLES"] = True
        tc.variables["NO_TUTORIALS"] = True
        tc.variables["NO_REGRESSION"] = True
        tc.variables["NO_TESTS"] = True
        tc.variables["NO_GLTESTS"] = True
        tc.variables["NO_MACOS_FRAMEWORK"] = True
        tc.generate()

    def build(self):
        if self.settings.os == "Macos" and not self._osd_gpu_enabled:
            path = os.path.join(self.source_folder, "opensubdiv", "CMakeLists.txt")
            replace_in_file(self, path, "$<TARGET_OBJECTS:osd_gpu_obj>", "")
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        if self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenSubdiv")
        target_suffix = "" if self.options.shared else "_static"

        self.cpp_info.components["osdcpu"].set_property("cmake_target_name", f"OpenSubdiv::osdcpu{target_suffix}")
        self.cpp_info.components["osdcpu"].libs = ["osdCPU"]
        if self.options.with_tbb:
            self.cpp_info.components["osdcpu"].requires = ["onetbb::onetbb"]

        if self._osd_gpu_enabled:
            self.cpp_info.components["osdgpu"].set_property("cmake_target_name", f"OpenSubdiv::osdgpu{target_suffix}")
            self.cpp_info.components["osdgpu"].libs = ["osdGPU"]
            dl_required = self.options.with_opengl or self.options.with_opencl
            if self.settings.os in ["Linux", "FreeBSD"] and dl_required:
                self.cpp_info.components["osdgpu"].system_libs = ["dl"]

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "OpenSubdiv"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenSubdiv"
        self.cpp_info.components["osdcpu"].names["cmake_find_package"] = f"osdcpu{target_suffix}"
        self.cpp_info.components["osdcpu"].names["cmake_find_package_multi"] = f"osdcpu{target_suffix}"
        self.cpp_info.components["osdgpu"].names["cmake_find_package"] = f"osdgpu{target_suffix}"
        self.cpp_info.components["osdgpu"].names["cmake_find_package_multi"] = f"osdgpu{target_suffix}"
