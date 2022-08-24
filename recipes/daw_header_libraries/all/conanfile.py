import os

from conan.errors import ConanInvalidConfiguration
from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.43.0"

class DawHeaderLibrariesConan(ConanFile):
    name = "daw_header_libraries"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Various header libraries mostly future std lib, replacements for(e.g. visit), or some misc"
    topics = ("algorithms", "helpers", "data-structures")
    homepage = "https://github.com/beached/header_libraries"
    settings = "compiler",
    generators = "cmake",
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
            tools.build.check_min_cppstd(self, self, "17")

        minimum_version = self._compiler_required_cpp17.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.scm.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{0} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def package(self):
        self.copy("LICENSE*", "licenses", self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "daw-header-libraries"
        self.cpp_info.filenames["cmake_find_package_multi"] = "daw-header-libraries"
        self.cpp_info.set_property("cmake_file_name", "daw-header-libraries")

        self.cpp_info.names["cmake_find_package"] = "daw"
        self.cpp_info.names["cmake_find_package_multi"] = "daw"
        self.cpp_info.set_property("cmake_target_name", "daw::daw-header-libraries")

        self.cpp_info.components["daw"].names["cmake_find_package"] = "daw-header-libraries"
        self.cpp_info.components["daw"].names["cmake_find_package_multi"] = "daw-header-libraries"
        self.cpp_info.components["daw"].set_property("cmake_target_name", "daw::daw-header-libraries")
