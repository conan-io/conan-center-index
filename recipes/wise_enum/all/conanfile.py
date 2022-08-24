from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class WiseEnumConan(ConanFile):
    name = "wise_enum"
    description = (
        "Header-only C++11/14/17 library provides static reflection for enums, "
        "work with any enum type without any boilerplate code."
    )
    topics = (
        "cplusplus",
        "enum-to-string",
        "string-to-enum"
        "serialization",
        "reflection",
        "header-only",
        "compile-time"
    )
    homepage = "https://github.com/quicknir/wise_enum"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSL-1.0"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, "11")

        compiler = str(self.settings.compiler)
        compiler_version = tools.scm.Version(self.settings.compiler.version)

        minimal_version = {
           "gcc": "5"
        }
        unsupported = {"Visual Studio"}
        if compiler in unsupported:
            raise ConanInvalidConfiguration(
                "{} does not support  {} compiler".format(self.name, compiler)
            )

        if compiler in minimal_version and compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "{} requires {} compiler {} or newer [is: {}]".format(self.name, compiler, minimal_version[compiler], compiler_version)
            )

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("*.h", dst="include", src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses" , src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "WiseEnum")
        self.cpp_info.set_property("cmake_target_name", "WiseEnum::wise_enum")
        self.cpp_info.set_property("pkg_config_name", "WiseEnum")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "WiseEnum"
        self.cpp_info.names["cmake_find_package_multi"] = "WiseEnum"
        self.cpp_info.names["pkg_config"] = "WiseEnum"
        self.cpp_info.components["_wise_enum"].names["cmake_find_package"] = "wise_enum"
        self.cpp_info.components["_wise_enum"].names["cmake_find_package_multi"] = "wise_enum"
        self.cpp_info.components["_wise_enum"].set_property("cmake_target_name", "WiseEnum::wise_enum")
        self.cpp_info.components["_wise_enum"].set_property("pkg_config_name", "WiseEnum")
