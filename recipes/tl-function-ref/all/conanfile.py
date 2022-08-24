from conan import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class TlfunctionrefConan(ConanFile):
    name = "tl-function-ref"
    description = "A lightweight, non-owning reference to a callable."
    license = "CC0-1.0"
    topics = ("function_ref", "callable")
    homepage = "https://github.com/TartanLlama/function_ref"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 14)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tl-function-ref")
        self.cpp_info.set_property("cmake_target_name", "tl::function-ref")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "tl-function-ref"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tl-function-ref"
        self.cpp_info.names["cmake_find_package"] = "tl"
        self.cpp_info.names["cmake_find_package_multi"] = "tl"
        self.cpp_info.components["function-ref"].names["cmake_find_package"] = "function-ref"
        self.cpp_info.components["function-ref"].names["cmake_find_package_multi"] = "function-ref"
        self.cpp_info.components["function-ref"].set_property("cmake_target_name", "tl::function-ref")
