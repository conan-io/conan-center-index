from conans import ConanFile, tools, CMake
import os


class GinkgoConan(ConanFile):
    name = "ginkgo"
    license = "BSD-3-Clause"
    homepage = "https://github.com/ginkgo-project/ginkgo"
    url = "https://github.com/conan-io/conan-center-index"
    description = "High-performance linear algebra library for manycore systems, with a focus on sparse solution of linear systems."
    topics = ("hpc", "linear-algebra")
    settings = {"os": None,
                "compiler": {"Visual Studio": {"runtime": None, "toolset": None,
                                               "version": ["16"]},
                             "gcc": {"exception": None, "libcxx": None,
                                     "threads": None,
                                     "version": [
                                         "5.4", "5.5", "6", "6.1", "6.2", "6.3",
                                         "6.4", "6.5", "7", "7.1", "7.2", "7.3",
                                         "7.4", "7.5", "8", "8.1", "8.2", "8.3",
                                         "8.4", "9", "9.1", "9.2", "9.3", "10",
                                         "10.1"]},
                             "clang": {"runtime": None, "libcxx": None,
                                       "version": [
                                           "3.9", "4.0", "5.0", "6.0", "7.0",
                                           "7.1", "8", "9", "10", "11"]},
                             "apple-clang": {"libcxx": None, "version": [
                                                 "10.0", "11.0", "12.0"]},
                             "intel": {"version": ["18", "19"]}},
                "build_type": None, "arch": None}
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

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
        debug_suffix = "d" if self.settings.build_type == "Debug" else ""

        self.cpp_info.components["reference"].libs = [
            "ginkgo_reference" + debug_suffix]
        self.cpp_info.components["cuda"].libs = ["ginkgo_cuda" + debug_suffix]
        self.cpp_info.components["hip"].libs = ["ginkgo_hip" + debug_suffix]

        self.cpp_info.components["omp"].libs = ["ginkgo_omp" + debug_suffix]
        self.cpp_info.components["omp"].requires = ["cuda", "hip"]

        self.cpp_info.components["core"].libs = ["ginkgo" + debug_suffix]
        self.cpp_info.components["core"].requires = [
            "reference", "omp", "cuda", "hip"]
