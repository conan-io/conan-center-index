from conans import ConanFile, tools
import os


class EnumFlagsConan(ConanFile):
    name = "enum-flags"
    description = "Bit flags for C++11 scoped enums"
    homepage = "https://github.com/grisumbras/enum-flags"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("bitmask", "enum")
    license = "MIT"
    options = {"disable_implicit_conversion": [True, False]}
    default_options = "disable_implicit_conversion=True"
    generators = "cmake"
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("include*", src=self._source_subfolder)
        self.copy("*LICENSE", dst="licenses", keep_path=False)

    def package_info(self):
        # Yes, there is a typo in the macro name.
        # This macro is only useful when using regular C enums,
        # since enum classes prevent implicit conversions already.
        if self.options.disable_implicit_conversion:
            self.cpp_info.defines = ["ENUM_CLASS_FLAGS_FORBID_IMPLICT_CONVERSION"]

    def package_id(self):
        self.info.header_only()
