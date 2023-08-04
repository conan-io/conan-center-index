import os.path

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=1.50.0"


class HictkConan(ConanFile):
    name = "hictk"
    description = "Blazing fast toolkit to work with .hic and .cool files"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/paulsengroup/hictk"
    topics = "hictk", "bioinformatics", "hic"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    options = {
        "with_eigen": [True, False]
    }
    default_options = {
        "with_eigen": True
    }

    @property
    def _minimum_cpp_standard(self):
        return 17

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fast_float/5.2.0")
        if self.options.with_eigen:
            self.requires("eigen/3.4.0")
        self.requires("fmt/10.0.0")
        self.requires("hdf5/1.14.0")
        self.requires("highfive/2.7.1")
        self.requires("libdeflate/1.18")
        self.requires("parallel-hashmap/1.3.11")
        self.requires("spdlog/1.12.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25 <4]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["HICTK_BUILD_BENCHMARKS"] = "OFF"
        tc.variables["HICTK_BUILD_EXAMPLES"] = "OFF"
        tc.variables["HICTK_BUILD_TOOLS"] = "OFF"
        tc.variables["HICTK_ENABLE_GIT_VERSION_TRACKING"] = "OFF"
        tc.variables["HICTK_ENABLE_TESTING"] = "OFF"
        tc.variables["HICTK_WITH_EIGEN"] = self.options.with_eigen
        tc.generate()

        cmakedeps = CMakeDeps(self)
        cmakedeps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "hictk")
        self.cpp_info.set_property("cmake_target_name", "hictk::libhictk")
        self.cpp_info.set_property("pkg_config_name", "hictk")

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "hictk"
        self.cpp_info.names["cmake_find_package_multi"] = "hictk"
