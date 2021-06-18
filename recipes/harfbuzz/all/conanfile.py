from conans import ConanFile, CMake, tools
import os


class HarfbuzzConan(ConanFile):
    name = "harfbuzz"
    description = "HarfBuzz is an OpenType text shaping engine."
    topics = ("conan", "harfbuzz", "opentype", "text", "engine")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://harfbuzz.org"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_freetype": [True, False],
        "with_icu": [True, False],
        "with_glib": [True, False],
        "with_gdi": [True, False],
        "with_uniscribe": [True, False],
        "with_directwrite": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_freetype": True,
        "with_icu": False,
        "with_glib": True,
        "with_gdi": True,
        "with_uniscribe": True,
        "with_directwrite": False
    }

    short_paths = True

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.with_gdi
            del self.options.with_uniscribe
            del self.options.with_directwrite

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_freetype:
            self.requires("freetype/2.10.4")
        if self.options.with_icu:
            self.requires("icu/68.2")
        if self.options.with_glib:
            self.requires("glib/2.68.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["HB_HAVE_FREETYPE"] = self.options.with_freetype
        self._cmake.definitions["HB_HAVE_GRAPHITE2"] = False
        self._cmake.definitions["HB_HAVE_GLIB"] = self.options.with_glib
        self._cmake.definitions["HB_HAVE_ICU"] = self.options.with_icu
        if tools.is_apple_os(self.settings.os):
            self._cmake.definitions["HB_HAVE_CORETEXT"] = True
        elif self.settings.os == "Windows":
            self._cmake.definitions["HB_HAVE_GDI"] = self.options.with_gdi
            self._cmake.definitions["HB_HAVE_UNISCRIBE"] = self.options.with_uniscribe
            self._cmake.definitions["HB_HAVE_DIRECTWRITE"] = self.options.with_directwrite
        self._cmake.definitions["HB_BUILD_UTILS"] = False
        self._cmake.definitions["HB_BUILD_SUBSET"] = False
        self._cmake.definitions["HB_HAVE_GOBJECT"] = False
        self._cmake.definitions["HB_HAVE_INTROSPECTION"] = False
        # fix for MinGW debug build
        if self.settings.compiler == "gcc" and self.settings.os == "Windows":
            self._cmake.definitions["CMAKE_C_FLAGS"] = "-Wa,-mbig-obj"
            self._cmake.definitions["CMAKE_CXX_FLAGS"] = "-Wa,-mbig-obj"

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "harfbuzz"
        self.cpp_info.names["cmake_find_package_multi"] = "harfbuzz"
        if self.options.with_icu:
            self.cpp_info.libs.append("harfbuzz-icu")
        self.cpp_info.libs.append("harfbuzz")
        self.cpp_info.includedirs.append(os.path.join("include", "harfbuzz"))
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.system_libs.append("user32")
            if self.options.with_gdi or self.options.with_uniscribe:
                self.cpp_info.system_libs.append("gdi32")
            if self.options.with_uniscribe or self.options.with_directwrite:
                self.cpp_info.system_libs.append("rpcrt4")
            if self.options.with_uniscribe:
                self.cpp_info.system_libs.append("usp10")
            if self.options.with_directwrite:
                self.cpp_info.system_libs.append("dwrite")
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["CoreFoundation", "CoreGraphics", "CoreText"])
        if not self.options.shared:
            libcxx = tools.stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
