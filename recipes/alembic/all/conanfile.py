from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


class AlembicConan(ConanFile):
    name = "alembic"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alembic/alembic"
    description = "Open framework for storing and sharing scene data."
    topics = ("3d", "scene", "geometry", "graphics")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_hdf5": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_hdf5": False,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("openexr/2.5.7")
        if self.options.with_hdf5:
            self.requires("hdf5/1.12.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["USE_ARNOLD"] = False
        self._cmake.definitions["USE_MAYA"] = False
        self._cmake.definitions["USE_PRMAN"] = False
        self._cmake.definitions["USE_PYALEMBIC"] = False
        self._cmake.definitions["USE_BINARIES"] = False
        self._cmake.definitions["USE_EXAMPLES"] = False
        self._cmake.definitions["USE_HDF5"] = self.options.with_hdf5
        self._cmake.definitions["USE_TESTS"] = False
        self._cmake.definitions["ALEMBIC_BUILD_LIBS"] = True
        self._cmake.definitions["ALEMBIC_ILMBASE_LINK_STATIC"] = True # for -DOPENEXR_DLL, handled by OpenEXR package
        self._cmake.definitions["ALEMBIC_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["ALEMBIC_USING_IMATH_3"] = False
        self._cmake.definitions["ALEMBIC_ILMBASE_FOUND"] = 1
        self._cmake.definitions["ALEMBIC_ILMBASE_LIBS"] = "OpenEXR::OpenEXR"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Alembic")
        self.cpp_info.set_property("cmake_target_name", "Alembic::Alembic")
        self.cpp_info.libs = ["Alembic"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Alembic"
        self.cpp_info.names["cmake_find_package_multi"] = "Alembic"
