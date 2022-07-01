from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class JsondtoConan(ConanFile):
    name = "json_dto"
    license = "BSD-3-Clause"
    homepage = "https://github.com/Stiffstream/json_dto"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A small header-only helper for converting data between json representation and c++ structs"
    topics = ("json", "dto", "serialization")
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("rapidjson/1.1.0")

    def validate(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "5",
            "clang": "4",
            "apple-clang": "8",
            "Visual Studio": "15"
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
        elif tools.Version(self.settings.compiler.version) < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

        if self.settings.compiler == "apple-clang" and tools.Version(self.settings.compiler.version) >= "11":
            raise ConanInvalidConfiguration(f"{self.name} requires apple-clang less then version 11")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = CMake(self)
        cmake.definitions["JSON_DTO_INSTALL"] = True
        cmake.definitions["JSON_DTO_FIND_DEPS"] = False
        cmake.configure(source_folder=os.path.join(self._source_subfolder, "dev", "json_dto"))
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "json-dto")
        self.cpp_info.set_property("cmake_target_name", "json-dto::json-dto")
        self.cpp_info.names["cmake_find_package"] = "json-dto"
        self.cpp_info.names["cmake_find_package_multi"] = "json-dto"
