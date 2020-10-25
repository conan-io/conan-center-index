import glob
import os

from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class SDFormat(ConanFile):
    name = "sdformat"
    license = "Apache-2.0"
    homepage = "http://sdformat.org/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Simulation Description Format (SDFormat) parser and description files."
    topics = ("ignition", "robotics", "simulation")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    generators = "cmake", "cmake_find_package_multi"
    exports_sources = "CMakeLists.txt"

    _cmake = None

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
        }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn(
                "{} recipe lacks information about the {} compiler support.".format(
                    self.name, self.settings.compiler
                )
            )
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires c++17 support. The current compiler {} {} does not support it.".format(
                        self.name,
                        self.settings.compiler,
                        self.settings.compiler.version,
                    )
                )

    def source(self):
        version_major = self.version.split('.')[0]
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("sdformat-sdformat{}_{}".format(version_major, self.version), self._source_subfolder)

    def requirements(self):
        self.requires("ignition-math/6.6.0")
        self.requires("tinyxml2/8.0.0")

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["USE_INTERNAL_URDF"] = True
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
            for dll_to_remove in glob.glob(os.path.join(self.package_folder, "bin", dll_pattern_to_remove)):
                os.remove(dll_to_remove)

    def package_info(self):
        version_major = self.version.split('.')[0]
        version_till_minor = ".".join(self.version.split(".")[0:2])
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "sdformat{}".format(version_major)
        self.cpp_info.names["cmake_find_package_multi"] = "sdformat{}".format(version_major)
        self.cpp_info.includedirs = ["include/sdformat-{}".format(version_till_minor)]
