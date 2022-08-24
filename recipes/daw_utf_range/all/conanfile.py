import os

from conan.errors import ConanInvalidConfiguration
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.43.0"

class DawUtfRangeConan(ConanFile):
    name = "daw_utf_range"
    description = "Range operations on character arrays"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/beached/utf_range/"
    topics = ("utf", "validator", "iterator")
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi", "cmake_find_package"
    no_copy_source = True

    _compiler_required_cpp17 = {
        "Visual Studio": "16",
        "gcc": "8",
        "clang": "7",
        "apple-clang": "12.0",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "17")

        minimum_version = self._compiler_required_cpp17.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))

    def requirements(self):
        self.requires("daw_header_libraries/2.68.1")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["DAW_USE_PACKAGE_MANAGEMENT"] = True
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def package(self):
        self.copy("LICENSE*", "licenses", self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "daw-utf-range"
        self.cpp_info.filenames["cmake_find_package_multi"] = "daw-utf-range"
        self.cpp_info.set_property("cmake_file_name", "daw-utf-range")
        self.cpp_info.names["cmake_find_package"] = "daw"
        self.cpp_info.names["cmake_find_package_multi"] = "daw"
        self.cpp_info.set_property("cmake_target_name", "daw::daw-utf-range")
        self.cpp_info.components["daw"].names["cmake_find_package"] = "daw-utf-range"
        self.cpp_info.components["daw"].names["cmake_find_package_multi"] = "daw-utf-range"
        self.cpp_info.components["daw"].set_property("cmake_target_name", "daw::daw-utf-range")
        self.cpp_info.components["daw"].requires = ["daw_header_libraries::daw"]
