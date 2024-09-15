from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import can_run, check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.scm import Version


class FaissRecipe(ConanFile):
    name = "faiss"
    package_type = "library"

    # Optional metadata
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Faiss - a library for efficient similarity search and clustering of dense vectors"
    topics = ("approximate-nearest-neighbor", "ann", "anns")
    homepage = "https://github.com/facebookresearch/faiss"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_opt_generic": [True, False],
        "with_opt_avx2": [True, False],
        "with_opt_avx512": [True, False],
        "with_gpu": [True, False],
        "with_c_api": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_opt_generic": False,
        "with_opt_avx2": True,
        "with_opt_avx512": False,
        "with_gpu": False,
        "with_c_api": False,
        # TODO: current openblas recipe does not export all below options yet
        # "openblas:use_openmp": True,
        # "openblas:use_thread": False,
        # "openblas:use_locking": False,
        # "openblas:num_threads": 512,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder,
            strip_root=True)
        apply_conandata_patches(self)

    @property
    def _enable_testing(self):
        return not self.conf.get("tools.build:skip_test", default=True, check_type=bool)

    def config_options(self):
        if self.settings.arch != "x86_64":
            del self.options.with_opt_avx2
            del self.options.with_opt_avx512
        if Version(self.version) < "1.8.0":
            del self.options.with_opt_avx512

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openblas/0.3.27")
        self.test_requires("gtest/1.12.1")

    def validate(self):
        if Version(self.version) < "1.8.0":
            check_min_cppstd(self, 11)
        if not (
            self.options.with_opt_generic or
            self.options.get_safe("with_opt_avx2", False) or
            self.options.get_safe("with_opt_avx512", False)
        ):
            raise ConanInvalidConfiguration("""Must configure at least one of following optimizations:
    - generic: no optimization
    - avx2: with x86 AVX2 instruction set
    - avx512 (only availible >=1.8.0): with x86 AVX512 instruction set
""")
        if not self.dependencies["openblas"].options.get_safe("use_openmp"):
            self.output.warning("Prefers openbals with use_openmp")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["FAISS_WITH_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["FAISS_WITH_OPT_GENERIC"] = self.options.with_opt_generic
        tc.variables["FAISS_WITH_OPT_AVX2"] = self.options.get_safe(
            "with_opt_avx2", False)
        tc.variables["FAISS_WITH_OPT_AVX512"] = self.options.get_safe(
            "with_opt_avx512", False)
        tc.variables["FAISS_ENABLE_GPU"] = self.options.with_gpu
        tc.variables["FAISS_ENABLE_RAFT"] = False
        tc.variables["FAISS_ENABLE_ROCM"] = False
        tc.variables["FAISS_ENABLE_PYTHON"] = False
        tc.variables["FAISS_ENABLE_C_API"] = self.options.with_c_api
        tc.variables["BUILD_TESTING"] = self._enable_testing
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if self._enable_testing:
            cmake.test()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", self.source_folder, self.package_folder)

    @property
    def _has_lib_gpu(self):
        return Version(self.version) >= "1.8.0" and (not self.options.shared) and self.options.get_safe("with_gpu", False)

    def _configure_component(self, opt, name):
        if not self.options.get_safe(opt, False):
            return

        self.cpp_info.components[name].libs = [name]
        self.cpp_info.components[name].requires = ["openblas::openblas"]
        if self._has_lib_gpu:
            self.cpp_info.components[f"{name}_gpu"].libs = ["faiss_gpu"]
            self.cpp_info.components[f"{name}_gpu"].requires = [name]

    def package_info(self):
        self._configure_component("with_opt_generic", "faiss")
        self._configure_component("with_opt_avx2", "faiss_avx2")
        self._configure_component("with_opt_avx512", "faiss_avx512")

    @property
    def _has_option_avx512(self):
        try:
            return hasattr(self.options, "with_opt_avx512")
        except:
            return False

    def compatibility(self):
        if self._has_option_avx512:
            return [{"options": [("with_opt_generic", True), ("with_opt_avx2", True), ("with_opt_avx512", True)]}]
        else:
            return [{"options": [("with_opt_generic", True), ("with_opt_avx2", True)]}]
