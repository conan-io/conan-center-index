from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class Toml11Conan(ConanFile):
    name = "toml11"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ToruNiina/toml11"
    description = "TOML for Modern C++"
    topics = ("toml", "c-plus-plus-11", "c-plus-plus", "parser", "serializer")
    license = "MIT"
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
        self.copy("toml.hpp", dst=os.path.join("include", "toml11"), src=self._source_subfolder)
        self.copy("*.hpp", dst=os.path.join("include", "toml11", "toml"), src=os.path.join(self._source_subfolder, "toml"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "toml11")
        self.cpp_info.set_property("cmake_target_name", "toml11::toml11")
        self.cpp_info.includedirs.append(os.path.join("include", "toml11"))
