import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.51.0"


class SdbusCppConan(ConanFile):
    name = "sdbus-cpp"
    license = "LicenseRef-LGPL-2.1-or-later-WITH-sdbus-cpp-LGPL-exception-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Kistler-Group/sdbus-cpp"
    description = "High-level C++ D-Bus library for Linux designed" \
                  " to provide easy-to-use yet powerful API in modern C++"
    topics = ("dbus", "sd-bus", "sdbus-c++")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_code_gen": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_code_gen": False,
    }
    generators = "PkgConfigDeps"

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "7",
            "clang": "6",
        }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder,
                 self.export_sources_folder)

    def configure(self):
        if Version(self.version) < "0.9.0":
            self.license = "LGPL-2.1-or-later"

        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.info.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.info.settings.compiler))
        else:
            if Version(self.info.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.info.settings.compiler, self.info.settings.compiler.version))
        if self.info.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux supported")

    def build_requirements(self):
        self.tool_requires("pkgconf/1.7.4")
        if self.options.with_code_gen:
            self.tool_requires("expat/2.4.8")

    def requirements(self):
        self.requires("libsystemd/251.4")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_CODE_GEN"] = self.options.with_code_gen
        tc.variables["BUILD_DOC"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_LIBSYSTEMD"] = False
        tc.generate()

        # workaround for https://gitlab.kitware.com/cmake/cmake/-/issues/18150
        copy(self, "*.pc", self.generators_folder,
             os.path.join(self.generators_folder, "lib", "pkgconfig"))

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        copy(self, "COPYING*", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sdbus-c++")
        self.cpp_info.components["sdbus-c++"].libs = ["sdbus-c++"]
        self.cpp_info.components["sdbus-c++"].requires.append(
            "libsystemd::libsystemd")
        self.cpp_info.components["sdbus-c++"].set_property(
            "cmake_target_name", "SDBusCpp::sdbus-c++")
        self.cpp_info.components["sdbus-c++"].set_property(
            "pkg_config_name", "sdbus-c++")
        self.cpp_info.components["sdbus-c++"].system_libs = [
            "pthread", "m"]

        if self.options.with_code_gen:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var with : {}".format(bin_path))
            self.buildenv_info.prepend_path("PATH", bin_path)

            # TODO: Remove in Conan 2.0 where Environment class will be required.
            self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "SDBusCpp"
        self.cpp_info.names["cmake_find_package_multi"] = "SDBusCpp"
        self.cpp_info.filenames["cmake_find_package"] = "sdbus-c++"
        self.cpp_info.filenames["cmake_find_package_multi"] = "sdbus-c++"
        self.cpp_info.components["sdbus-c++"].names["cmake_find_package"] = "sdbus-c++"
        self.cpp_info.components["sdbus-c++"].names["cmake_find_package_multi"] = "sdbus-c++"
        self.cpp_info.components["sdbus-c++"].names["pkg_config"] = "sdbus-c++"
