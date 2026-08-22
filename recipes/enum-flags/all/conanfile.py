from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class EnumFlagsConan(ConanFile):
    name = "enum-flags"
    description = "Bit flags for C++11 scoped enums"
    homepage = "https://github.com/grisumbras/enum-flags"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("bitmask", "enum")
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "forbid_implicit_conversions": [True, False],
    }
    default_options = {
        "forbid_implicit_conversions": True,
    }

    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "enumflags")
        self.cpp_info.set_property("cmake_target_name", "EnumFlags::EnumFlags")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        # Yes, there is a typo in the macro name.
        # This macro is only useful when using regular C enums,
        # since enum classes prevent implicit conversions already.
        if self.options.forbid_implicit_conversions:
            self.cpp_info.defines = ["ENUM_CLASS_FLAGS_FORBID_IMPLICT_CONVERSION"]

        # TODO: to remove in conan v2
        self.cpp_info.filenames["cmake_find_package"] = "enumflags"
        self.cpp_info.filenames["cmake_find_package_multi"] = "enumflags"
        self.cpp_info.names["cmake_find_package"] = "EnumFlags"
        self.cpp_info.names["cmake_find_package_multi"] = "EnumFlags"
