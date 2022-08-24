from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class BitseryConan(ConanFile):
    name = "bitsery"
    description = (
        "Header only C++ binary serialization library. It is designed around "
        "the networking requirements for real-time data delivery, especially for games."
    )
    topics = ("serialization", "binary", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/fraillt/bitsery"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "11")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Bitsery")
        self.cpp_info.set_property("cmake_target_name", "Bitsery::bitsery")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Bitsery"
        self.cpp_info.names["cmake_find_package_multi"] = "Bitsery"
        self.cpp_info.components["bitserylib"].names["cmake_find_package"] = "bitsery"
        self.cpp_info.components["bitserylib"].names["cmake_find_package_multi"] = "bitsery"
