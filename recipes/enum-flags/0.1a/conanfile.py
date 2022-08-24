from conan import ConanFile, tools$
import os

required_conan_version = ">=1.28.0"

class EnumFlagsConan(ConanFile):
    name = "enum-flags"
    description = "Bit flags for C++11 scoped enums"
    homepage = "https://github.com/grisumbras/enum-flags"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("bitmask", "enum")
    license = "MIT"
    settings = "compiler"
    options = {"forbid_implicit_conversions": [True, False]}
    default_options = {"forbid_implicit_conversions": True}
    generators = "cmake"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("include*", src=self._source_subfolder)
        self.copy("*LICENSE", dst="licenses", keep_path=False)

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "enumflags"
        self.cpp_info.filenames["cmake_find_package_multi"] = "enumflags"
        self.cpp_info.names["cmake_find_package"] = "EnumFlags"
        self.cpp_info.names["cmake_find_package_multi"] = "EnumFlags"
        # Yes, there is a typo in the macro name.
        # This macro is only useful when using regular C enums,
        # since enum classes prevent implicit conversions already.
        if self.options.forbid_implicit_conversions:
            self.cpp_info.defines = ["ENUM_CLASS_FLAGS_FORBID_IMPLICT_CONVERSION"]
