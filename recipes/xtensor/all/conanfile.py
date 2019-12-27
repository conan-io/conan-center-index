import os

from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class XtensorConan(ConanFile):
    name = "xtensor"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xtensor-stack/xtensor"
    description = "C++ tensors with broadcasting and lazy computing"
    topics = ("conan", "numpy", "multidimensional-arrays", "tensors")
    options = {"xsimd": [True, False], "tbb": [True, False], "openmp": [True, False]}
    default_options = {"xsimd": True, "tbb": False, "openmp": False}
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def configure(self):
        if self.options.tbb and self.options.openmp:
            raise ConanInvalidConfiguration(
                "The options 'tbb' and 'openmp' can not be used together."
            )

    def requirements(self):
        self.requires("xtl/0.6.9")
        self.requires("nlohmann_json/3.7.3")
        if self.options.xsimd:
            self.requires.add("xsimd/7.4.4")
        if self.options.tbb:
            self.requires.add("tbb/2019_u9")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(
            "*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include")
        )

    def package_info(self):
        if self.options.xsimd:
            self.cpp_info.defines.append("XTENSOR_USE_XSIMD")
        if self.options.tbb:
            self.cpp_info.defines.append("XTENSOR_USE_TBB")
        if self.options.openmp:
            self.cpp_info.defines.append("XTENSOR_USE_OPENMP")
