import os
from conans import ConanFile, CMake, tools


class TaoCPPTupleConan(ConanFile):
    name = "taocpp-tuple"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/tuple"
    description = "Compile-time-efficient proof-of-concept implementation for std::tuple"
    topics = ("template", "cpp11", "tuple")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "tuple-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        cmake = CMake(self)
        cmake.definitions["TAOCPP_TUPLE_BUILD_TESTS"] = False
        cmake.definitions["TAOCPP_TUPLE_INSTALL_DOC_DIR"] = "licenses"
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()
