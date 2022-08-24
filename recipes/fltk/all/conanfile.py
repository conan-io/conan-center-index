from from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"

class FltkConan(ConanFile):
    name = "fltk"
    description = "Fast Light Toolkit is a cross-platform C++ GUI toolkit"
    topics = ("fltk", "gui")
    homepage = "https://www.fltk.org"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-2.0-custom"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_gl": [True, False],
        "with_threads": [True, False],
        "with_gdiplus": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_gl": True,
        "with_threads": True,
        "with_gdiplus": True,
    }
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.with_gdiplus

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.12")
        self.requires("libjpeg/9d")
        self.requires("libpng/1.6.37")
        if self.settings.os == "Linux":
            self.requires("opengl/system")
            self.requires("glu/system")
            self.requires("fontconfig/2.13.93")
            self.requires("xorg/system")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['OPTION_BUILD_SHARED_LIBS'] = self.options.shared
        cmake.definitions['FLTK_BUILD_TEST'] = False
        cmake.definitions['FLTK_BUILD_EXAMPLES'] = False
        cmake.definitions['OPTION_USE_GL'] = self.options.with_gl
        cmake.definitions['OPTION_USE_THREADS'] = self.options.with_threads
        cmake.definitions['OPTION_BUILD_HTML_DOCUMENTATION'] = False
        cmake.definitions['OPTION_BUILD_PDF_DOCUMENTATION'] = False
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "FLTK.framework"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "CMake"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "fltk-config*")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fltk")
        self.cpp_info.set_property("cmake_target_name", "fltk::fltk")

        self.cpp_info.names["cmake_find_package"] = "fltk"
        self.cpp_info.names["cmake_find_package_multi"] = "fltk"

        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("FL_DLL")
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os in ("Linux", "FreeBSD"):
            if self.options.with_threads:
                self.cpp_info.system_libs.extend(['pthread', 'dl'])
            if self.options.with_gl:
                self.cpp_info.system_libs.extend(['GL', 'GLU'])
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ['Cocoa', 'OpenGL', 'IOKit', 'Carbon', 'CoreFoundation', 'CoreVideo']
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = [
                "gdi32",
                "imm32",
                "msimg32",
                "ole32",
                "oleaut32",
                "uuid",
            ]
            if self.options.get_safe("with_gdiplus"):
                self.cpp_info.system_libs.append("gdiplus")
