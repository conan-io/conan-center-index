from conan import ConanFile, tools
from conans import CMake
from conan.tools.microsoft import is_msvc
import os
import functools

required_conan_version = ">=1.33.0"

class DimeConan(ConanFile):
    name = "dime"
    description = "DXF (Data eXchange Format) file format support library."
    topics = ("dxf", "coin3d", "opengl", "graphics")
    homepage = "https://github.com/coin3d/dime"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake",
    settings = "os", "arch", "compiler", "build_type",
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "fixbig": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "fixbig": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, "11")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["DIME_BUILD_SHARED_LIBS"] = self.options.shared
        if self.options.fixbig:
            cmake.definitions["CMAKE_CXX_FLAGS"] = "-DDIME_FIXBIG"
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "configure_file(${CMAKE_SOURCE_DIR}/${PROJECT_NAME_LOWER}.pc.cmake.in ${CMAKE_BINARY_DIR}/${PROJECT_NAME_LOWER}.pc @ONLY)",
            "configure_file(${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT_NAME_LOWER}.pc.cmake.in ${CMAKE_BINARY_DIR}/${PROJECT_NAME_LOWER}.pc @ONLY)")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.settings.os == "Windows" and is_msvc(self):
            tools.files.rm(self, "*.pdb", self.package_folder)

    def package_info(self):
        libname = "dime"
        if self.settings.os == "Windows" and is_msvc(self):
            libname = "{}{}{}{}".format(
                libname,
                tools.scm.Version(self.version).major,
                "" if self.options.shared else "s",
                "d" if self.settings.build_type == "Debug" else "",
                )
        self.cpp_info.libs = [libname]

        if self.settings.os == "Windows":
            self.cpp_info.cxxflags.append("-DDIME_DLL" if self.options.shared else "-DDIME_NOT_DLL")
        if self.options.fixbig:
            self.cpp_info.cxxflags.append("-DDIME_FIXBIG")

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
