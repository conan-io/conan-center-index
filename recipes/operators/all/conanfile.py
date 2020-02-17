import os
from conans import ConanFile, CMake, tools


class TaoCPPOperatorsConan(ConanFile):
    name = "operators"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/operators"
    description = "A highly efficient, move-aware operators library"
    topics = ("cpp", "cpp11", "header-only", "operators")
    generators = "cmake"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        cmake = CMake(self)
        cmake.definitions["TAOCPP_OPERATORS_BUILD_TESTS"] = False
        cmake.definitions["TAOCPP_OPERATORS_INSTALL_DOC_DIR"] = "licenses"
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()
