from conans import ConanFile, tools

required_conan_version = ">=1.33.0"

class Thelink2012AnyConan(ConanFile):
    name = "thelink2012-any"
    license = "BSL-1.0"
    description = "Implementation of std::experimental::any, including small object optimization, for C++11 compilers"
    topics = ("any", "c++11", "data-structures")
    homepage = "https://github.com/thelink2012/any"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE*", "licenses", self._source_subfolder)
        self.copy("any.hpp", "include", self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "any"
        self.cpp_info.names["cmake_find_package_multi"] = "any"
        self.cpp_info.set_property("cmake_target_name", "any::any")
