from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class TaoCPPOperatorsConan(ConanFile):
    name = "taocpp-operators"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/operators"
    description = "A highly efficient, move-aware operators library"
    topics = ("cpp", "cpp11", "header-only", "operators")
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "taocpp-operators")
        self.cpp_info.set_property("cmake_target_name", "taocpp::operators")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "taocpp-operators"
        self.cpp_info.filenames["cmake_find_package_multi"] = "taocpp-operators"
        self.cpp_info.names["cmake_find_package"] = "taocpp"
        self.cpp_info.names["cmake_find_package_multi"] = "taocpp"
        self.cpp_info.components["_taocpp-operators"].names["cmake_find_package"] = "operators"
        self.cpp_info.components["_taocpp-operators"].names["cmake_find_package_multi"] = "operators"
        self.cpp_info.components["_taocpp-operators"].set_property("cmake_target_name", "taocpp::operators")
