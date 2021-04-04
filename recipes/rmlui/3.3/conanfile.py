from conans import ConanFile, CMake, tools
import os


class RmluiConan(ConanFile):
    name = "rmlui"
    description = "RmlUi - The HTML/CSS User Interface Library Evolved"
    homepage = "https://github.com/mikke89/RmlUi"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    topics = ("conan", "css", "gui", "html", "lua", "rmlui")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "build_lua_bindings": [True, False],
        "build_samples": [True, False],
        "disable_rtti_and_exceptions": [True, False],
        "enable_precompiled_headers": [True, False],
        "enable_tracy_profiling": [True, False],
        "fPIC": [True, False],
        "no_font_interface_default": [True, False],
        "no_thirdparty_containers": [True, False],
        "shared": [True, False]
    }
    default_options = {
        "build_lua_bindings": False,
        "build_samples": False,
        "disable_rtti_and_exceptions": False,
        "enable_precompiled_headers": True,
        "enable_tracy_profiling": False,
        "fPIC": True,
        "no_font_interface_default": False,
        "no_thirdparty_containers": False,
        "shared": False
    }
    generators = "cmake_find_package"

    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if not self.options.no_font_interface_default:
            self.requires("freetype/2.10.1")

        if self.options.build_lua_bindings:
            self.requires("lua/5.3.5")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if not hasattr(self, "_cmake"):
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_LUA_BINDINGS"] = self.options.build_lua_bindings
            self._cmake.definitions["BUILD_SAMPLES"] = self.options.build_samples
            self._cmake.definitions["DISABLE_RTTI_AND_EXCEPTIONS"] = self.options.disable_rtti_and_exceptions
            self._cmake.definitions["ENABLE_PRECOMPILED_HEADERS"] = self.options.enable_precompiled_headers
            self._cmake.definitions["ENABLE_TRACY_PROFILING"] = self.options.enable_tracy_profiling
            self._cmake.definitions["NO_FONT_INTERFACE_DEFAULT"] = self.options.no_font_interface_default
            self._cmake.definitions["NO_THIRDPARTY_CONTAINERS"] = self.options.no_thirdparty_containers

            self._cmake.configure(source_folder=self._source_subfolder)

        return self._cmake

    def _patch_sources(self):
        # The *.cmake files that conan generates using cmake_find_package for CMake's find_package to consume use
        # different variable naming than described in CMake's documentation, thus the need for most of the replacements.
        # References:
        #  * https://cmake.org/cmake/help/latest/module/FindFreetype.html
        #  * https://cmake.org/cmake/help/latest/module/FindLua.html
        replace_mapping = {
            "FREETYPE_FOUND": "Freetype_FOUND",
            "FREETYPE_INCLUDE_DIRS": "Freetype_INCLUDE_DIRS",
            "FREETYPE_LINK_DIRS": "Freetype_LINK_DIRS",
            "FREETYPE_LIBRARY": "Freetype_LIBRARIES",
            "LUA_FOUND": "lua_FOUND",
            "LUA_INCLUDE_DIR": "lua_INCLUDE_DIR",
            "LUA_LIBRARIES": "lua_LIBRARIES",
            # disables the built-in generation of package configuration files
            "if(PkgHelpers_AVAILABLE)": "if(FALSE)"
        }

        cmakelists_path = os.path.join(
            self._source_subfolder, "CMakeLists.txt")

        for key, value in replace_mapping.items():
            tools.replace_in_file(cmakelists_path, key, value)

    def build(self):
        self._patch_sources()
        self._configure_cmake().build()

    def package(self):
        self._configure_cmake().install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        if self.options.disable_rtti_and_exceptions:
            self.cpp_info.defines.append("RMLUI_USE_CUSTOM_RTTI")

        if self.options.no_thirdparty_containers:
            self.cpp_info.defines.append("RMLUI_NO_THIRDPARTY_CONTAINERS")

        if not self.options.shared:
            self.cpp_info.defines.append("RMLUI_STATIC_LIB")

        self.cpp_info.libs.append("RmlDebugger")

        if self.options.build_lua_bindings:
            self.cpp_info.libs.append("RmlControlsLua")
        self.cpp_info.libs.append("RmlControls")

        if self.options.build_lua_bindings:
            self.cpp_info.libs.append("RmlCoreLua")
        self.cpp_info.libs.append("RmlCore")
