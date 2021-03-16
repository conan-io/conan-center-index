from conans import ConanFile, tools, CMake
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

    def config_options(self):
        if self.settings.os == "Windows":
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
        self._cmake.definitions["GINKGO_SKIP_DEPENDENCY_UPDATE"] = True
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_Git"] = True
        self._cmake.definitions["GINKGO_BUILD_REFERENCE"] = True
        self._cmake.definitions["GINKGO_BUILD_OMP"] = self.options.openmp
        self._cmake.definitions["GINKGO_BUILD_CUDA"] = self.options.cuda
        self._cmake.definitions["GINKGO_BUILD_HIP"] = False
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        if "fPIC" in self.options:
            self._cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
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
        self.cpp_info.libs = tools.collect_libs(self)
