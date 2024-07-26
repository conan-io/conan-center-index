import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, replace_in_file
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class GpuCppConan(ConanFile):
    name = "gpu.cpp"
    description = "A lightweight library for portable low-level GPU computation using WebGPU."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gpucpp.answer.ai/"
    topics = ("gpgpu", "webgpu")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
            "msvc": "192",
            "Visual Studio": "16",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("dawn/cci.20240726")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        pkg_includes = os.path.join(self.package_folder, "include", "gpu.cpp")
        copy(self, "gpu.h", self.source_folder, pkg_includes)
        copy(self, "*.h", os.path.join(self.source_folder, "numeric_types"), os.path.join(pkg_includes, "numeric_types"))
        copy(self, "*.h", os.path.join(self.source_folder, "utils"), os.path.join(pkg_includes, "utils"))

        # Fix incompatibility with newer Dawn
        replace_in_file(self, os.path.join(pkg_includes, "gpu.h"),
                        "WGPUBufferUsageFlags",
                        "WGPUBufferUsage")

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
