import os.path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.50.0"


class HictkConan(ConanFile):
    name = "hictk"
    description = "Blazing fast toolkit to work with .hic and .cool files"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/paulsengroup/hictk"
    topics = "hictk", "bioinformatics", "hic"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_arrow": [True, False],
        "with_eigen": [True, False]
    }
    default_options = {
        "with_arrow": False,
        "with_eigen": True
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "11",
            "clang": "7",
            "gcc": "8",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if Version(self.version) < "1.0.0":
            del self.options.with_arrow

    def requirements(self):
        if self.options.get_safe("with_arrow"):
            self.requires("arrow/16.1.0")
        self.requires("bshoshany-thread-pool/4.1.0")
        self.requires("fast_float/6.1.1")
        if self.options.with_eigen:
            self.requires("eigen/3.4.0")
        self.requires("fmt/10.2.1")
        self.requires("hdf5/1.14.3")
        self.requires("highfive/2.9.0")
        self.requires("libdeflate/1.20")
        self.requires("parallel-hashmap/1.3.12")  # Note: v1.3.12 is more recent than v1.37
        self.requires("span-lite/0.11.0")
        self.requires("spdlog/1.14.1")
        self.requires("zstd/[>=1.5 <1.6]")

        if Version(self.version) == "0.0.3":
            self.requires("xxhash/0.8.2")

        if Version(self.version) > "0.0.7":
            self.requires("readerwriterqueue/1.0.6")
            self.requires("concurrentqueue/1.0.4")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["HICTK_BUILD_BENCHMARKS"] = "OFF"
        tc.variables["HICTK_BUILD_EXAMPLES"] = "OFF"
        tc.variables["HICTK_BUILD_TOOLS"] = "OFF"
        tc.variables["HICTK_ENABLE_GIT_VERSION_TRACKING"] = "OFF"
        tc.variables["HICTK_ENABLE_TESTING"] = "OFF"
        tc.variables["HICTK_WITH_ARROW"] = self.options.get_safe("with_arrow", False)
        tc.variables["HICTK_WITH_EIGEN"] = self.options.with_eigen
        tc.generate()

        cmakedeps = CMakeDeps(self)
        cmakedeps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "hictk")
        self.cpp_info.set_property("cmake_target_name", "hictk::libhictk")

        if self.options.get_safe("with_arrow"):
            self.cpp_info.defines.append("HICTK_WITH_ARROW")
        if self.options.with_eigen:
            self.cpp_info.defines.append("HICTK_WITH_EIGEN")
