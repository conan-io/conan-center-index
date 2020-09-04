import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.28.0"

class TaoCPPPEGTLConan(ConanFile):
    name = "taocpp-pegtl"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/pegtl"
    description = "Parsing Expression Grammar Template Library"
    topics = ("peg", "header-only", "cpp",
              "parsing", "cpp17", "cpp11", "grammar")
    no_copy_source = True
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "PEGTL-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        cmake = CMake(self)
        cmake.definitions["PEGTL_BUILD_TESTS"] = False
        cmake.definitions["PEGTL_BUILD_EXAMPLES"] = False
        cmake.definitions["PEGTL_INSTALL_DOC_DIR"] = "licenses"
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "pegtl"
        self.cpp_info.filenames["cmake_find_package_multi"] = "pegtl"
        self.cpp_info.names["cmake_find_package"] = "taocpp"
        self.cpp_info.names["cmake_find_package_multi"] = "taocpp"
        self.cpp_info.components["_taocpp-pegtl"].names["cmake_find_package"] = "pegtl"
        self.cpp_info.components["_taocpp-pegtl"].names["cmake_find_package_multi"] = "pegtl"
