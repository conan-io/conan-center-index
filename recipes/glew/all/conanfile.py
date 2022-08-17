from conan import ConanFile
from conan.tools import files
from conans import CMake
import functools
import os

required_conan_version = ">=1.43.0"


class GlewConan(ConanFile):
    name = "glew"
    description = "The GLEW library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://github.com/nigels-com/glew"
    topics = ("glew", "opengl", "wrangler", "loader", "binding")
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_egl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_egl": False,
    }

    generators = "cmake"

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
            del self.options.with_egl

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("opengl/system")
        self.requires("glu/system")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_UTILS"] = False
        cmake.definitions["GLEW_EGL"] = self.options.get_safe("with_egl", False)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        files.apply_conandata_patches(self)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        files.rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        glewlib_target_name = "glew" if self.options.shared else "glew_s"
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "GLEW")
        self.cpp_info.set_property("cmake_file_name", "glew")
        self.cpp_info.set_property("cmake_target_name", "GLEW::GLEW")
        self.cpp_info.set_property("pkg_config_name", "glew")
        self.cpp_info.components["glewlib"].set_property("cmake_module_target_name", "GLEW::GLEW")
        self.cpp_info.components["glewlib"].set_property("cmake_target_name", f"GLEW::{glewlib_target_name}")
        self.cpp_info.components["glewlib"].set_property("pkg_config_name", "glew")

        if self.settings.os == "Windows":
            lib_name = "glew32" if self.options.shared else "libglew32"
        else:
            lib_name = "GLEW"
        if self.settings.build_type == "Debug":
            lib_name += "d"
        self.cpp_info.components["glewlib"].libs = [lib_name]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.components["glewlib"].defines.append("GLEW_STATIC")
        self.cpp_info.components["glewlib"].requires = ["opengl::opengl", "glu::glu"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "GLEW"
        self.cpp_info.filenames["cmake_find_package_multi"] = "glew"
        self.cpp_info.names["cmake_find_package"] = "GLEW"
        self.cpp_info.names["cmake_find_package_multi"] = "GLEW"
        self.cpp_info.components["glewlib"].names["cmake_find_package"] = "GLEW"
        self.cpp_info.components["glewlib"].names["cmake_find_package_multi"] = glewlib_target_name
