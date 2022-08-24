from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.33.0"


class ProCxxBoostExSimdConan(ConanFile):
    name = "procxx-boost-ext-simd"
    description = ("Portable SIMD computation library - was proposed as a "
                   "Boost library"
                   )
    homepage = "https://github.com/procxx/boost.simd"
    topics = ("conan", "boost", "simd")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _min_cppstd(self):
        return "11"

    def requirements(self):
        self.requires("boost/1.76.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self._min_cppstd)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_folder = "boost.simd-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def package(self):
        self.copy(pattern="*", dst="include",
                  src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        # this technique was inspired by conan-center's "boost-ex-ut" recipe,
        # and has been fixed to use the upstream Capitalized `Boost::`
        # namespace for components
        self.cpp_info.names["cmake_find_package"] = "Boost"
        self.cpp_info.names["cmake_find_package_multi"] = "Boost"

        # The original find_package() name here:
        self.cpp_info.filenames["cmake_find_package"] = "Boost.SIMD"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Boost.SIMD"
        self.cpp_info.components["SIMD"].names["cmake_find_package"] = "SIMD"
        self.cpp_info.components["SIMD"].names["cmake_find_package_multi"] = \
            "SIMD"
        self.cpp_info.components["SIMD"].requires = ["boost::headers"]
