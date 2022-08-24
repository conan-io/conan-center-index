from conan.tools.microsoft import msvc_runtime_flag
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class GinkgoConan(ConanFile):
    name = "ginkgo"
    license = "BSD-3-Clause"
    homepage = "https://github.com/ginkgo-project/ginkgo"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "High-performance linear algebra library for manycore systems, with a "
        "focus on sparse solution of linear systems."
    )
    topics = ("hpc", "linear-algebra")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "openmp": [True, False],
        "cuda": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": False,
        "openmp": False,
        "cuda": False,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "5.4",
            "clang": "3.9",
            "apple-clang": "10.0",
            "intel": "18"
        }

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                "{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard,
                    self.settings.compiler, self.settings.compiler.version
                )
            )

        if self.options.shared and self._is_msvc and "MT" in msvc_runtime_flag(self):
            raise ConanInvalidConfiguration(
                "Ginkgo does not support mixing static CRT and shared library"
            )

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["GINKGO_BUILD_TESTS"] = False
        self._cmake.definitions["GINKGO_BUILD_EXAMPLES"] = False
        self._cmake.definitions["GINKGO_BUILD_BENCHMARKS"] = False
        self._cmake.definitions["GINKGO_DEVEL_TOOLS"] = False
        self._cmake.definitions["GINKGO_BUILD_REFERENCE"] = True
        self._cmake.definitions["GINKGO_BUILD_OMP"] = self.options.openmp
        self._cmake.definitions["GINKGO_BUILD_CUDA"] = self.options.cuda
        self._cmake.definitions["GINKGO_BUILD_HIP"] = False
        self._cmake.definitions["GINKGO_BUILD_DPCPP"] = False
        self._cmake.definitions["GINKGO_BUILD_HWLOC"] = False
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Ginkgo")
        self.cpp_info.set_property("cmake_target_name", "Ginkgo::ginkgo")
        self.cpp_info.set_property("pkg_config_name", "ginkgo")

        debug_suffix = "d" if self.settings.build_type == "Debug" else ""
        has_dpcpp_device = tools.Version(self.version) >= "1.4.0"

        self.cpp_info.components["ginkgo_core"].set_property("cmake_target_name", "Ginkgo::ginkgo")
        self.cpp_info.components["ginkgo_core"].set_property("pkg_config_name", "ginkgo")
        self.cpp_info.components["ginkgo_core"].libs = [
            "ginkgo" + debug_suffix]
        self.cpp_info.components["ginkgo_core"].requires = [
            "ginkgo_omp", "ginkgo_cuda", "ginkgo_reference", "ginkgo_hip"
        ]

        self.cpp_info.components["ginkgo_cuda"].set_property("cmake_target_name", "Ginkgo::ginkgo_cuda")
        self.cpp_info.components["ginkgo_cuda"].libs = [
            "ginkgo_cuda" + debug_suffix]
        self.cpp_info.components["ginkgo_cuda"].requires = ["ginkgo_hip"]

        self.cpp_info.components["ginkgo_omp"].set_property("cmake_target_name", "Ginkgo::ginkgo_omp")
        self.cpp_info.components["ginkgo_omp"].libs = [
            "ginkgo_omp" + debug_suffix]
        self.cpp_info.components["ginkgo_omp"].requires = [
            "ginkgo_cuda", "ginkgo_hip"]

        self.cpp_info.components["ginkgo_hip"].set_property("cmake_target_name", "Ginkgo::ginkgo_hip")
        self.cpp_info.components["ginkgo_hip"].libs = [
            "ginkgo_hip" + debug_suffix]

        self.cpp_info.components["ginkgo_reference"].set_property("cmake_target_name", "Ginkgo::ginkgo_reference")
        self.cpp_info.components["ginkgo_reference"].libs = [
            "ginkgo_reference" + debug_suffix]

        if has_dpcpp_device: # Always add these components
            # See https://github.com/conan-io/conan-center-index/pull/7044#discussion_r698181588
            self.cpp_info.components["ginkgo_core"].requires += ["ginkgo_dpcpp"]
            self.cpp_info.components["ginkgo_core"].requires += ["ginkgo_device"]

            self.cpp_info.components["ginkgo_dpcpp"].set_property("cmake_target_name", "Ginkgo::ginkgo_dpcpp")
            self.cpp_info.components["ginkgo_dpcpp"].libs = [
                "ginkgo_dpcpp" + debug_suffix]

            self.cpp_info.components["ginkgo_device"].set_property("cmake_target_name", "Ginkgo::ginkgo_device")
            self.cpp_info.components["ginkgo_device"].libs = [
                "ginkgo_device" + debug_suffix]

            self.cpp_info.components["ginkgo_omp"].requires += [
                "ginkgo_dpcpp", "ginkgo_device"]
            self.cpp_info.components["ginkgo_reference"].requires += ["ginkgo_device"]
            self.cpp_info.components["ginkgo_hip"].requires += ["ginkgo_device"]
            self.cpp_info.components["ginkgo_cuda"].requires += ["ginkgo_device"]
            self.cpp_info.components["ginkgo_dpcpp"].requires += ["ginkgo_device"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Ginkgo"
        self.cpp_info.names["cmake_find_package_multi"] = "Ginkgo"
        self.cpp_info.components["ginkgo_core"].names["cmake_find_package"] = "ginkgo"
        self.cpp_info.components["ginkgo_core"].names["cmake_find_package_multi"] = "ginkgo"
