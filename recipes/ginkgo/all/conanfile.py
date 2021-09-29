from conans import ConanFile, tools, CMake
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration
import os


class GinkgoConan(ConanFile):
    name = "ginkgo"
    license = "BSD-3-Clause"
    homepage = "https://github.com/ginkgo-project/ginkgo"
    url = "https://github.com/conan-io/conan-center-index"
    description = "High-performance linear algebra library for manycore systems, with a focus on sparse solution of linear systems."
    topics = ("hpc", "linear-algebra")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "openmp": [
        True, False], "cuda": [True, False]}
    default_options = {"shared": False, "fPIC": False,
                       "openmp": False, "cuda": False}
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/**"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))
            if self.settings.compiler == "Visual Studio":
                static_crt = str(
                    self.settings.compiler.runtime).startswith("MT")
                if static_crt and self.options.shared:
                    raise ConanInvalidConfiguration(
                        "Ginkgo does not support mixing static CRT and shared library")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

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
        for patch in self.conan_data["patches"][self.version]:
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
        self.cpp_info.names["cmake_find_package"] = "Ginkgo"
        self.cpp_info.names["cmake_find_package_multi"] = "Ginkgo"
        self.cpp_info.names["pkg_config"] = "ginkgo"

        debug_suffix = "d" if self.settings.build_type == "Debug" else ""
        has_dpcpp_device = Version(self.version) >= Version("1.4.0")

        self.cpp_info.components["ginkgo_core"].names["cmake_find_package"] = "ginkgo"
        self.cpp_info.components["ginkgo_core"].names["cmake_find_package_multi"] = "ginkgo"
        self.cpp_info.components["ginkgo_core"].names["pkg_config"] = "ginkgo"
        self.cpp_info.components["ginkgo_core"].libs = [
            "ginkgo" + debug_suffix]
        self.cpp_info.components["ginkgo_core"].requires = [
            "ginkgo_omp", "ginkgo_cuda", "ginkgo_reference", "ginkgo_hip"
        ]

        self.cpp_info.components["ginkgo_cuda"].names["cmake_find_package"] = "ginkgo_cuda"
        self.cpp_info.components["ginkgo_cuda"].names["cmake_find_package_multi"] = "ginkgo_cuda"
        self.cpp_info.components["ginkgo_cuda"].libs = [
            "ginkgo_cuda" + debug_suffix]
        self.cpp_info.components["ginkgo_cuda"].requires = ["ginkgo_hip"]

        self.cpp_info.components["ginkgo_omp"].names["cmake_find_package"] = "ginkgo_omp"
        self.cpp_info.components["ginkgo_omp"].names["cmake_find_package_multi"] = "ginkgo_omp"
        self.cpp_info.components["ginkgo_omp"].libs = [
            "ginkgo_omp" + debug_suffix]
        self.cpp_info.components["ginkgo_omp"].requires = [
            "ginkgo_cuda", "ginkgo_hip"]

        self.cpp_info.components["ginkgo_hip"].names["cmake_find_package"] = "ginkgo_hip"
        self.cpp_info.components["ginkgo_hip"].names["cmake_find_package_multi"] = "ginkgo_hip"
        self.cpp_info.components["ginkgo_hip"].libs = [
            "ginkgo_hip" + debug_suffix]

        self.cpp_info.components["ginkgo_reference"].names["cmake_find_package"] = "ginkgo_reference"
        self.cpp_info.components["ginkgo_reference"].names["cmake_find_package_multi"] = "ginkgo_reference"
        self.cpp_info.components["ginkgo_reference"].libs = [
            "ginkgo_reference" + debug_suffix]

        if has_dpcpp_device: # Always add these components
            # See https://github.com/conan-io/conan-center-index/pull/7044#discussion_r698181588
            self.cpp_info.components["ginkgo_core"].requires += ["ginkgo_dpcpp"]
            self.cpp_info.components["ginkgo_core"].requires += ["ginkgo_device"]

            self.cpp_info.components["ginkgo_dpcpp"].names["cmake_find_package"] = "ginkgo_dpcpp"
            self.cpp_info.components["ginkgo_dpcpp"].names["cmake_find_package_multi"] = "ginkgo_dpcpp"
            self.cpp_info.components["ginkgo_dpcpp"].libs = [
                "ginkgo_dpcpp" + debug_suffix]

            self.cpp_info.components["ginkgo_device"].names["cmake_find_package"] = "ginkgo_device"
            self.cpp_info.components["ginkgo_device"].names["cmake_find_package_multi"] = "ginkgo_device"
            self.cpp_info.components["ginkgo_device"].libs = [
                "ginkgo_device" + debug_suffix]

            self.cpp_info.components["ginkgo_omp"].requires += [
                "ginkgo_dpcpp", "ginkgo_device"]
            self.cpp_info.components["ginkgo_reference"].requires += ["ginkgo_device"]
            self.cpp_info.components["ginkgo_hip"].requires += ["ginkgo_device"]
            self.cpp_info.components["ginkgo_cuda"].requires += ["ginkgo_device"]
            self.cpp_info.components["ginkgo_dpcpp"].requires += ["ginkgo_device"]
