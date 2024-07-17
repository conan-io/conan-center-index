from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rmdir
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.52.0"


class TinyADConan(ConanFile):
    name = "tinyad"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/patr-schm/TinyAD"
    description = "TinyAD is a C++ header-only library for second-order automatic differentiation"
    topics = ("algebra", "linear-algebra", "optimization", "autodiff", "numerical", "header-only")
    package_type = "header-library"
    license = ("MIT")

    settings = "os", "arch", "compiler", "build_type"
    options = {"with_openmp": [True, False]}
    default_options = {"with_openmp": True}

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)
        if self.options.with_openmp and self.settings.compiler in ["clang", "apple-clang"]:
            self.requires("llvm-openmp/18.1.8", transitive_headers=True, transitive_libs=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "include/**", src=self.source_folder, dst=self.package_folder)
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    @property
    def _openmp_flags(self):
        if self.settings.compiler == "clang":
            return ["-fopenmp=libomp"]
        elif self.settings.compiler == "apple-clang":
            return ["-Xclang", "-fopenmp"]
        elif self.settings.compiler == "gcc":
            return ["-fopenmp"]
        elif self.settings.compiler == "intel-cc":
            return ["-Qopenmp"]
        elif self.settings.compiler == "sun-cc":
            return ["-xopenmp"]
        elif is_msvc(self):
            return ["-openmp"]
        return None

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TinyAD")
        self.cpp_info.set_property("cmake_target_name", "TinyAD")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # OpenMP preprocessor directives are used in a number of headers
        if self.options.with_openmp:
            if self.settings.compiler in ["clang", "apple-clang"]:
                self.cpp_info.requires.append("llvm-openmp::llvm-openmp")
            openmp_flags = self._openmp_flags
            self.cpp_info.cflags.extend(openmp_flags)
            self.cpp_info.cxxflags.extend(openmp_flags)
            self.cpp_info.exelinkflags.extend(openmp_flags)
            self.cpp_info.sharedlinkflags.extend(openmp_flags)
