import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, collect_libs, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class EckitConan(ConanFile):
    name = "eckit"
    description = "C++ toolkit for ECMWF tools and applications"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ecmwf/eckit"
    topics = ("toolkit", "ecmwf")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
        "with_curl": [True, False],
        "with_omp": [True, False],
        "with_mpi": [True, False],
        "with_bzip2": [True, False],
        "with_lz4": [True, False],
        "with_snappy": [True, False],
        "with_aec": [True, False],
        "with_zip": [True, False],
        "with_xxhash": [True, False],
        "with_proj": [True, False],
        "with_lapack": [True, False],
        "with_mkl": [True, False],
        "with_eigen": [True, False],
        "with_qhull": [True, False],
        "with_shapelib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
        "with_curl": True,
        "with_omp": True,
        "with_mpi": True,
        "with_bzip2": True,
        "with_lz4": True,
        "with_snappy": True,
        "with_aec": True,
        "with_zip": True,
        "with_xxhash": True,
        "with_proj": True,
        "with_lapack": False,
        "with_mkl": False,
        "with_eigen": False,
        "with_qhull": False,
        "with_shapelib": False,
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

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.with_curl:
            self.requires("libcurl/[>=7.78.0 <9]")
        if self.options.with_mpi:
            self.requires("openmpi/[>=4.0]")
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.with_lz4:
            self.requires("lz4/1.10.0")
        if self.options.with_snappy:
            self.requires("snappy/1.2.1")
        if self.options.with_aec:
            self.requires("libaec/1.1.4")
        if self.options.with_zip:
            self.requires("libzip/1.11.4")
        if self.options.with_xxhash:
            self.requires("xxhash/0.8.3")
        if self.options.with_proj:
            self.requires("proj/9.7.0")
        if self.options.with_lapack:
            self.requires("openblas/0.3.30")
        if self.options.with_eigen:
            self.requires("eigen/3.4.1")
        if self.options.with_qhull:
            self.requires("qhull/8.0.2")
        if self.options.with_shapelib:
            self.requires("shapelib/1.6.1")

    def build_requirements(self):
        self.tool_requires("ecbuild/3.14.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_SSL"] = self.options.with_openssl
        tc.variables["ENABLE_CURL"] = self.options.with_curl
        tc.variables["ENABLE_OMP"] = self.options.with_omp
        tc.variables["ENABLE_MPI"] = self.options.with_mpi
        tc.variables["ENABLE_BZIP2"] = self.options.with_bzip2
        tc.variables["ENABLE_LZ4"] = self.options.with_lz4
        tc.variables["ENABLE_SNAPPY"] = self.options.with_snappy
        tc.variables["ENABLE_AEC"] = self.options.with_aec
        tc.variables["ENABLE_ZIP"] = self.options.with_zip
        tc.variables["ENABLE_XXHASH"] = self.options.with_xxhash
        tc.variables["ENABLE_PROJ"] = self.options.with_proj
        tc.variables["ENABLE_LAPACK"] = self.options.with_lapack
        tc.variables["ENABLE_MKL"] = self.options.with_mkl
        tc.variables["ENABLE_EIGEN"] = self.options.with_eigen
        tc.variables["ENABLE_CONVEX_HULL"] = self.options.with_qhull
        tc.variables["ENABLE_GEO_AREA_SHAPEFILE"] = self.options.with_shapelib
        
        if self.options.with_mpi:
            tc.variables["MPI_C_LIBRARIES"] = "MPI::MPI_C"
        tc.variables["ENABLE_PKGCONFIG"] = False
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        
        tc.variables["BUILD_TESTING"] = False
        tc.variables["ENABLE_TESTS"] = False
        tc.variables["ENABLE_EXTRA_TESTS"] = False
        tc.variables["ENABLE_AIO"] = False
        tc.variables["ENABLE_CUDA"] = False
        tc.variables["ENABLE_HIP"] = False
        tc.variables["ENABLE_TORCH"] = False
        tc.variables["ENABLE_RADOS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        self.output.info(f"source_folder: {self.source_folder}")
        self.output.info(f"build_folder: {self.build_folder}")
        import re
        for root, _, files in os.walk(self.source_folder):
            for f in files:
                if f == "CMakeLists.txt":
                    filepath = os.path.join(root, f)
                    with open(filepath, "r", encoding="utf-8") as file:
                        content = file.read()
                    new_content, count = re.subn(r"TYPE\s+SHARED", "", content)
                    if count > 0:
                        self.output.info(f"Replaced {count} occurrences in {filepath}")
                    with open(filepath, "w", encoding="utf-8") as file:
                        file.write(new_content)
        
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "eckit")
        self.cpp_info.set_property("cmake_target_name", "eckit")
        
        all_libs = [
            "eckit_geo",
            "eckit_sql",
            "eckit_web",
            "eckit_distributed",
            "eckit_mpi",
            "eckit_linalg",
            "eckit_geometry",
            "eckit_maths",
            "eckit_option",
            "eckit_spec",
            "eckit_codec",
            "eckit_cmd",
            "eckit",
        ]
        collected = collect_libs(self)
        self.cpp_info.libs = [lib for lib in all_libs if lib in collected] + [lib for lib in collected if lib not in all_libs]
        self.cpp_info.includedirs = ["include"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "dl", "m", "rt"])
