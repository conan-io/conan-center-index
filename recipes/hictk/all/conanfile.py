import os.path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
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
    options = {"with_eigen": [True, False]}
    default_options = {"with_eigen": True}

    @property
    def _minimum_cpp_standard(self):
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

    def requirements(self):
        self.requires("bshoshany-thread-pool/3.5.0", transitive_headers=True)
        self.requires("fast_float/5.3.0", transitive_headers=True)
        if self.options.with_eigen:
            self.requires("eigen/3.4.0", transitive_headers=True)
        self.requires("fmt/10.1.1", transitive_headers=True)
        self.requires("hdf5/1.14.1", transitive_headers=True)
        self.requires("highfive/2.7.1", transitive_headers=True)
        self.requires("libdeflate/1.19", transitive_headers=True)
        self.requires("parallel-hashmap/1.37", transitive_headers=True)
        self.requires("span-lite/0.10.3", transitive_headers=True)
        self.requires("spdlog/1.12.0", transitive_headers=True)
        self.requires("xxhash/0.8.2", transitive_headers=True)
        self.requires("zstd/1.5.5", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        compiler = str(self.settings.compiler)
        version = str(self.settings.compiler.version)
        try:
            minimum_version = self._compilers_minimum_version[str(compiler)]
            if minimum_version and loose_lt_semver(version, minimum_version):
                msg = (
                    f"{self.ref} requires C++{self._minimum_cpp_standard} features "
                    f"which are not supported by compiler {compiler} {version}."
                )
                raise ConanInvalidConfiguration(msg)
        except KeyError:
            msg = (
                f"{self.ref} recipe lacks information about the {compiler} compiler, "
                f"support for the required C++{self._minimum_cpp_standard} features is assumed"
            )
            self.output.warn(msg)

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
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "hictk")
        self.cpp_info.set_property("cmake_target_name", "hictk::libhictk")
        self.cpp_info.set_property("pkg_config_name", "hictk")

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "hictk"
        self.cpp_info.names["cmake_find_package_multi"] = "hictk"
