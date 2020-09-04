import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.28.0"

class TaoCPPOperatorsConan(ConanFile):
    name = "taocpp-operators"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/operators"
    description = "A highly efficient, move-aware operators library"
    topics = ("cpp", "cpp11", "header-only", "operators")
    no_copy_source = True
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "operators-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        cmake = CMake(self)
        cmake.definitions["TAOCPP_OPERATORS_BUILD_TESTS"] = False
        cmake.definitions["TAOCPP_OPERATORS_INSTALL_DOC_DIR"] = "licenses"
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "taocpp-operators"
        self.cpp_info.filenames["cmake_find_package_multi"] = "taocpp-operators"
        self.cpp_info.names["cmake_find_package"] = "taocpp"
        self.cpp_info.names["cmake_find_package_multi"] = "taocpp"
        self.cpp_info.components["_taocpp-operators"].names["cmake_find_package"] = "operators"
        self.cpp_info.components["_taocpp-operators"].names["cmake_find_package_multi"] = "operators"
