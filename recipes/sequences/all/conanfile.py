import os
from conans import ConanFile, CMake, tools


class TaoCPPSequencesonan(ConanFile):
    name = "taocpp-sequences"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "hhttps://github.com/taocpp/sequences"
    description = "Variadic templates and std::integer_sequence support library"
    topics = ("variadic-template", "template", "interger-sequence")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "sequences-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        cmake = CMake(self)
        cmake.definitions["TAOCPP_SEQUENCES_BUILD_TESTS"] = False
        cmake.definitions["TAOCPP_SEQUENCES_INSTALL_DOC_DIR"] = "licenses"
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()
