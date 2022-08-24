from from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration


import os


class BertrandConan(ConanFile):
    name = "bertrand"
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bernedom/bertrand"
    description = "A C++ header only library providing a trivial implementation for design by contract."
    topics = ("design by contract", "dbc",
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
            "Visual Studio": "15.7",
            "clang": "5",
            "apple-clang": "10",
        }

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, "17")
        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False)
        if minimum_version:
            if tools.scm.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("bertrand requires C++17, which your compiler ({} {}) does not support.".format(
                    self.settings.compiler, self.settings.compiler.version))
        else:
            self.output.warn(
                "bertrand requires C++17. Your compiler is unknown. Assuming it supports C++17.")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_folder = "bertrand-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = CMake(self)
        cmake.definitions["BERTRAND_BUILD_TESTING"] = False
        cmake.definitions["BERTRAND_INSTALL_LIBRARY"] = True
        cmake.configure(build_folder=self._build_subfolder)
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
