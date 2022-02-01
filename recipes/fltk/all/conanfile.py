from conans import CMake, ConanFile, tools
import os, shutil, glob

required_conan_version = ">=1.33.0"

class FltkConan(ConanFile):
    name = "fltk"
    description = "Fast Light Toolkit is a cross-platform C++ GUI toolkit"
    topics = ("fltk", "gui")
    homepage = "https://www.fltk.org"
    license = "LGPL-2.0-custom"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package_multi"
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.with_gdiplus

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.11")
        self.requires("libjpeg/9d")
        self.requires("libpng/1.6.37")
        if self.settings.os == "Linux":
            self.requires("opengl/system")
            self.requires("glu/system")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['OPTION_BUILD_SHARED_LIBS'] = self.options.shared
        cmake.definitions['OPTION_BUILD_EXAMPLES'] = False
        cmake.definitions['OPTION_USE_GL'] = self.options.with_gl
        cmake.definitions['OPTION_USE_THREADS'] = self.options.with_threads
        cmake.definitions['OPTION_USE_SYSTEM_ZLIB'] = False
        cmake.definitions['OPTION_USE_SYSTEM_LIBJPEG'] = False
        cmake.definitions['OPTION_USE_SYSTEM_LIBPNG'] = False
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(self._source_subfolder + "/COPYING", dst="licenses", keep_path=False, ignore_case=True)
        # # these headers and libs come from dependencies
        # deps_includes = self.package_folder + "/include/FL/images"
        # if os.path.isdir(deps_includes):
        #     shutil.rmtree(deps_includes)
        # removed_libs = ["z", "jpeg", "png"]
        # for rlib in removed_libs:
        #     for fn in glob.glob(self.package_folder + "/*/*fltk_" + rlib + "*.*"):
        #         os.remove(fn)       # lib/fltk_png.lib, bin/libfltk_png_SHARED.dll
        # if self.options.shared:
        #     for fn in glob.glob(self.package_folder + "/lib/*.lib"):
        #         if '_SHARED' not in fn:
        #             os.remove(fn)   # static libraries
        tools.remove_from_path(os.path.join(self.package_folder, "share", "fltk"))

    def package_info(self):
        if self.options.shared:
            self.cpp_info.defines.append("FL_DLL")
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ['m', 'dl', 'X11', 'Xext']
            if self.options.with_threads:
                self.cpp_info.system_libs.extend(['pthread'])
            if self.options.with_gl:
                self.cpp_info.system_libs.extend(['GL', 'GLU'])
        if self.settings.os == "Windows" and self.options.get_safe("with_gdiplus"):
            self.cpp_info.system_libs = [
                "gdiplus",
                "uuid",
                "msimg32",
                "gdi32",
                "imm32",
                "ole32",
                "oleaut32"
            ]

