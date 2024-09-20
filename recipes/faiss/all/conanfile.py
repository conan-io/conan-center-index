import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import stdcpp_library, check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, save, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"

class FaissRecipe(ConanFile):
    name = "faiss"
    description = "Faiss - a library for efficient similarity search and clustering of dense vectors"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facebookresearch/faiss"
    topics = ("approximate-nearest-neighbor", "similarity-search", "clustering", "gpu")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "opt_level": ["generic", "avx2", "avx512"],
        "enable_c_api": [True, False],
        "enable_gpu": [False, "cuda"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "opt_level": "avx2",
        "enable_c_api": False,
        "enable_gpu": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "5",
            "apple-clang": "9",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "*.cmake", self.recipe_folder, self.export_sources_folder)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],  strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # TODO: current openblas recipe does not export all below options yet
        # self.options["openblas"].use_openmp = True
        # self.options["openblas"].use_thread = False
        # self.options["openblas"].use_locking = False
        # self.options["openblas"].num_threads = 512

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openblas/0.3.27")
        self.requires("openmp/system")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if self.settings.arch != "x86_64" and self.options.opt_level != "generic":
            raise ConanInvalidConfiguration(f"-o opt_level={self.options.opt_level} is only supported on x86_64")
        if self.options.enable_gpu and not self.options.shared:
            raise ConanInvalidConfiguration(f"-o enable_gpu={self.options.enable_gpu} is only supported with -o shared=True")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <4]")

    def generate(self):
        VirtualBuildEnv(self).generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["FAISS_OPT_LEVEL"] = self.options.opt_level
        tc.cache_variables["FAISS_ENABLE_C_API"] = self.options.enable_c_api
        tc.cache_variables["FAISS_ENABLE_GPU"] = bool(self.options.enable_gpu)
        tc.cache_variables["FAISS_ENABLE_RAFT"] = False
        tc.cache_variables["FAISS_ENABLE_PYTHON"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Disable irrelevant subdirs
        save(self, os.path.join(self.source_folder, "demos", "CMakeLists.txt"), "")
        save(self, os.path.join(self.source_folder, "benchs", "CMakeLists.txt"), "")
        save(self, os.path.join(self.source_folder, "tutorial", "cpp", "CMakeLists.txt"), "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.options.enable_gpu:
            copy(self, "faiss-cuda-support.cmake",
                 self.export_sources_folder,
                 os.path.join(self.package_folder, "lib", "cmake", "faiss"))

    @property
    def _enabled_opt_levels(self):
        levels = self.__class__.options["opt_level"]
        return levels[:levels.index(self.options.opt_level) + 1]

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "faiss")

        for level in self._enabled_opt_levels:
            lib = "faiss" if level == "generic" else f"faiss_{level}"
            component = self.cpp_info.components[lib]
            component.set_property("cmake_target_name", lib)
            component.libs = [lib]
            component.requires = ["openblas::openblas", "openmp::openmp"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                component.system_libs.append("m")
            if self.options.enable_gpu:
                component.builddirs = [os.path.join("lib", "cmake", "faiss")]

        if self.options.enable_c_api:
            self.cpp_info.components["faiss_c"].set_property("cmake_target_name", "faiss_c")
            self.cpp_info.components["faiss_c"].libs = ["faiss_c"]
            self.cpp_info.components["faiss_c"].requires = ["faiss"]
            if not self.options.shared and stdcpp_library(self):
                self.cpp_info.components["faiss_c"].system_libs.append(stdcpp_library(self))

        if self.options.enable_gpu:
            cmake_module = os.path.join("lib", "cmake", "faiss", "faiss-cuda-support.cmake")
            self.cpp_info.set_property("cmake_build_modules", [cmake_module])

    def compatibility(self):
        levels = self.__class__.options["opt_level"]
        compatible_levels = levels[levels.index(self.options.opt_level)+1:]
        return [{"options": [("opt_level", level)]} for level in compatible_levels]
