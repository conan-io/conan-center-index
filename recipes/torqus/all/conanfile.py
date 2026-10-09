from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os

required_conan_version = ">=2"


class TorqusConan(ConanFile):
    name = "torqus"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rysolis/torqus"
    description = "A C++20 TFHE library (leveled arithmetic, gate bootstrapping)"
    topics = ("tfhe", "fhe", "homomorphic-encryption", "cryptography", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    options = {
        "use_mimalloc": [True, False],
        "enable_simd": [True, False],
        "enable_noise": [True, False],
    }
    default_options = {
        "use_mimalloc": True,
        "enable_simd": True,
        "enable_noise": True,
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Optional even in the CMakeLists.txt sense (falls back to the
        # system allocator if not found) -- only actually required() here
        # because Conan needs to resolve/build it up front when the option
        # is on, unlike CMake's own find_package(... QUIET) probe.
        if self.options.use_mimalloc:
            self.requires("mimalloc/3.3.2")

    def package_id(self):
        # Header-only, so settings (os/arch/compiler/build_type) don't
        # affect the package -- nothing here gets compiled. Options are a
        # different story: use_mimalloc is baked into the installed
        # torqusConfig.cmake's find guard, and enable_simd/enable_noise
        # become INTERFACE compile definitions exported via
        # torqusTargets.cmake, so different option values really do
        # produce different installed package content and must stay part
        # of the package_id.
        self.info.settings.clear()

    def validate(self):
        check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["TORQUS_USE_MIMALLOC"] = bool(self.options.use_mimalloc)
        tc.variables["TORQUS_ENABLE_SIMD"] = bool(self.options.enable_simd)
        tc.variables["TFHE_ENABLE_NOISE"] = bool(self.options.enable_noise)
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "torqus")
        self.cpp_info.set_property("cmake_target_name", "torqus::torqus")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
