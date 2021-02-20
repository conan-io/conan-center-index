from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

class So5extraConan(ConanFile):
    name = "so5extra"
    license = "BSD-3-Clause"
    homepage = "https://github.com/Stiffstream/so5extra"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A collection of various SObjectizer's extensions."
    topics = ("concurrency", "actor-framework", "actors", "agents", "sobjectizer")
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("sobjectizer/5.7.2.2")

    def configure(self):
        minimal_cpp_standard = "17"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "Visual Studio": "15"
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return

        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["SO5EXTRA_INSTALL"] = True

        self._cmake.configure(source_folder=os.path.join(self._source_subfolder, "dev", "so_5_extra"))
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-v." + self.version
        os.rename(extracted_dir, self._source_subfolder )

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "so5extra"
        self.cpp_info.filenames["cmake_find_package_multi"] = "so5extra"
        self.cpp_info.names["cmake_find_package"] = "sobjectizer"
        self.cpp_info.names["cmake_find_package_multi"] = "sobjectizer"
        self.cpp_info.components["so_5_extra"].name = "so5extra"
        self.cpp_info.components["so_5_extra"].requires = ["sobjectizer::sobjectizer"]

