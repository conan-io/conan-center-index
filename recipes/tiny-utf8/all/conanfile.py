from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class Tinyutf8Conan(ConanFile):
    name = "tiny-utf8"
    description = "Tiny-utf8 is a library for extremely easy integration of Unicode into an arbitrary C++11 project."
    license = "BSD-3-Clause"
    topics = ("tiny-utf8", "utf8")
    homepage = "https://github.com/DuffsDevice/tiny-utf8"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENCE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tinyutf8")
        self.cpp_info.set_property("cmake_target_name", "tinyutf8::tinyutf8")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "tinyutf8"
        self.cpp_info.names["cmake_find_package_multi"] = "tinyutf8"
