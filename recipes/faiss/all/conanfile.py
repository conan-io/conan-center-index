import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir, replace_in_file

required_conan_version = ">=2.0.9"


class FaissConan(ConanFile):
    name = "faiss"
    description = "Faiss is a library for efficient similarity search and clustering of dense vectors"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facebookresearch/faiss"
    topics = ("approximate-nearest-neighbor", "gpu")
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

    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openblas/0.3.27")
        self.requires("gflags/2.2.2")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <4]")

    def validate(self):
        check_min_cppstd(self, 17)

        if self.settings.compiler == "apple-clang":
            raise ConanInvalidConfiguration("OpenMP support is required, which is not "
                                            "available in Apple Clang")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD", "##set(CMAKE_CXX_STANDARD")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["FAISS_ENABLE_GPU"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["FAISS_ENABLE_PYTHON"] = False
        tc.cache_variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = str(self.settings.build_type)

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["faiss"]

        self.cpp_info.set_property("cmake_file_name", "faiss")
        self.cpp_info.set_property("cmake_target_name", "faiss")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "dl"]

        if not self.options.shared and self.settings.compiler in ("clang", "gcc"):
            self.cpp_info.exelinkflags.append("-fopenmp")
            self.cpp_info.sharedlinkflags.append("-fopenmp")
