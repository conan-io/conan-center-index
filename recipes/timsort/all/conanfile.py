from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class TimsortConan(ConanFile):
    name = "timsort"
    description = "A C++ implementation of timsort"
    topics = ("timsort", "sorting", "algorithms")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/timsort/cpp-TimSort"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            if tools.scm.Version(self.version) >= "2.0.0":
                tools.build.check_min_cppstd(self, self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "gfx-timsort")
        self.cpp_info.set_property("cmake_target_name", "gfx::timsort")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "gfx-timsort"
        self.cpp_info.filenames["cmake_find_package_multi"] = "gfx-timsort"
        self.cpp_info.names["cmake_find_package"] = "gfx"
        self.cpp_info.names["cmake_find_package_multi"] = "gfx"
        self.cpp_info.components["gfx-timsort"].names["cmake_find_package"] = "timsort"
        self.cpp_info.components["gfx-timsort"].names["cmake_find_package_multi"] = "timsort"
        self.cpp_info.components["gfx-timsort"].set_property("cmake_target_name", "gfx::timsort")
