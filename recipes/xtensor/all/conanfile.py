import os

from conans import CMake, ConanFile, tools


class XtensorConan(ConanFile):
    name = "xtensor"
    license = "BSD 3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    repo_url = "https://github.com/xtensor-stack/xtensor"
    description = "C++ tensors with broadcasting and lazy computing"
    topics = ("conan", "numpy", "multidimensional-arrays", "tensors")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    options = {"xsimd": [True, False], "tbb": [True, False], "openmp": [True, False]}
    default_options = {"xsimd": True, "tbb": False, "openmp": False}
    exports_sources = "CMakeLists.txt"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def requirements(self):
        self.requires("xtl/0.6.9")
        if self.options.xsimd:
            self.requires.add("xsimd/7.4.4")
        if self.options.tbb:
            self.requires.add("tbb/2019_u9")
        if self.options.openmp:
            pass

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["XTENSOR_USE_XSIMD"] = self.options.xsimd
        cmake.definitions["XTENSOR_USE_TBB"] = self.options.tbb
        cmake.definitions["XTENSOR_USE_OPENMP"] = self.options.openmp
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_id(self):
        self.info.header_only()
