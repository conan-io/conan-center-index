from from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=1.43.0"

class SiConan(ConanFile):
    name = "si"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bernedom/SI"
    description = "A header only c++ library that provides type safety and user defined literals \
         for handling pyhsical values defined in the International System of Units."
    topics = ("physical units", "SI-unit-conversion",
              "cplusplus-library", "cplusplus-17")
    exports_sources = "CMakeLists.txt"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15",
            "clang": "5",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, "17")

        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False)
        if minimum_version:
            if tools.scm.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("'si' requires C++17, which your compiler ({} {}) does not support.".format(
                    self.settings.compiler, self.settings.compiler.version))
        else:
            self.output.warn(
                "'si' requires C++17. Your compiler is unknown. Assuming it supports C++17.")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = CMake(self)
        cmake.definitions["SI_BUILD_TESTING"] = False
        cmake.definitions["SI_BUILD_DOC"] = False
        cmake.definitions["SI_INSTALL_LIBRARY"] = True
        cmake.configure(build_folder=self._build_subfolder)
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "SI::SI")

        self.cpp_info.names["cmake_find_package"] = "SI"
        self.cpp_info.names["cmake_find_package_multi"] = "SI"
