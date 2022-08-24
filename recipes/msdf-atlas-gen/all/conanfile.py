from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.33.0"


class MsdfAtlasGenConan(ConanFile):
    name = "msdf-atlas-gen"
    license = "MIT"
    homepage = "https://github.com/Chlumsky/msdf-atlas-gen"
    url = "https://github.com/conan-io/conan-center-index"
    description = "MSDF font atlas generator"
    topics = ("msdf-atlas-gen", "msdf", "font", "atlas")
    settings = "os", "arch", "compiler", "build_type"

    generators = "cmake", "cmake_find_package_multi"
    exports_sources = ["CMakeLists.txt"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("artery-font-format/1.0")
        self.requires("msdfgen/1.9.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        cmakelists = os.path.join(
            self._source_subfolder, "CMakeLists.txt")

        tools.files.replace_in_file(self, cmakelists,
                              "add_subdirectory(msdfgen)", "")
        tools.save_append(cmakelists,
                          "install(TARGETS msdf-atlas-gen-standalone DESTINATION bin)")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["MSDF_ATLAS_GEN_BUILD_STANDALONE"] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libdirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
