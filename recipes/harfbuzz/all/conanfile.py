from conans import ConanFile, CMake, tools
import os


class HarfbuzzConan(ConanFile):
    name = "harfbuzz"
    description = "HarfBuzz is an OpenType text shaping engine."
    topics = ("conan", "harfbuzz", "opentype", "text", "engine")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://harfbuzz.org"
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "patches/*.patch"]
    generators = "cmake"
    short_paths = True

    settings = "os", "arch", "compiler", "build_type"
    
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_freetype": [True, False],
        "with_icu": [True, False],
        "with_glib": [True, False],
        "with_gdi": [True, False],
        "with_uniscribe": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_freetype": True,
        "with_icu": False,
        "with_glib": True,
        "with_gdi": True,
        "with_uniscribe": True
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    _cmake = None

    def requirements(self):
        if self.options.with_freetype:
            self.requires("freetype/2.10.2")
        if self.options.with_icu:
            self.requires("icu/67.1")
        if self.options.with_glib:
            self.requires("glib/2.66.0")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.with_gdi
            del self.options.with_uniscribe

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake_compiler_flags(self, cmake):
        flags = []
        compiler = str(self.settings.compiler)
        if compiler in ("clang", "apple-clang"):
            flags.append("-Wno-deprecated-declarations")
        if self.settings.compiler == "gcc" and self.settings.os == "Windows":
            flags.append("-Wa,-mbig-obj")
        cmake.definitions["CMAKE_C_FLAGS"] = " ".join(flags)
        cmake.definitions["CMAKE_CXX_FLAGS"] = cmake.definitions["CMAKE_C_FLAGS"]

        return cmake

    def _configure_cmake_macos(self, cmake):
        if tools.is_apple_os(self.settings.os):
            cmake.definitions["CMAKE_MACOSX_RPATH"] = True
        return cmake

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake = self._configure_cmake_compiler_flags(self._cmake)
        self._cmake = self._configure_cmake_macos(self._cmake)
        self._cmake.definitions["HB_HAVE_FREETYPE"] = self.options.with_freetype
        self._cmake.definitions["HB_BUILD_TESTS"] = False
        self._cmake.definitions["HB_HAVE_ICU"] = self.options.with_icu
        self._cmake.definitions["HB_HAVE_GLIB"] = self.options.with_glib

        if self.settings.os == "Windows":
            self._cmake.definitions["HB_HAVE_GDI"] = self.options.with_gdi
            self._cmake.definitions["HB_HAVE_UNISCRIBE"] = self.options.with_uniscribe

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for p in self.conan_data["patches"][self.version]:
            tools.patch(**p)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "harfbuzz"))
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.system_libs.extend(["dwrite", "rpcrt4", "usp10", "gdi32", "user32"])
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["CoreFoundation", "CoreGraphics", "CoreText"])
