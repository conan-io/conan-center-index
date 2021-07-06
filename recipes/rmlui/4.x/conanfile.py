from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
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
        "enable_rtti_and_exceptions": [True, False],
        "font_interface": ["freetype", None],
        "fPIC": [True, False],
        "matrix_mode": ["column_major", "row_major"],
        "shared": [True, False],
        "with_lua_bindings": [True, False],
        "with_thirdparty_containers": [True, False]
    }
    default_options = {
        "enable_rtti_and_exceptions": True,
        "font_interface": "freetype",
        "fPIC": True,
        "matrix_mode": "column_major",
        "shared": False,
        "with_lua_bindings": False,
        "with_thirdparty_containers": True
    }
    build_requires = ["cmake/3.20.0"]
    exports_sources = ["CMakeLists.txt"]
    generators = ["cmake", "cmake_find_package"]

    @property
    def _minimum_compilers_version(self):
        # Reference: https://en.cppreference.com/w/cpp/compiler_support/14
        return {
            "apple-clang": "5.1",
            "clang": "3.4",
            "gcc": "5",
            "intel": "17",
            "sun-cc": "5.15",
            "Visual Studio": "15"
        }

    @property
    def _minimum_cpp_standard(self):
        return 14

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        
        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if lazy_lt_semver(str(self.settings.compiler.version), min_version):
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))

    def requirements(self):
        if self.options.font_interface == "freetype":
            self.requires("freetype/2.10.1")

        if self.options.with_lua_bindings:
            self.requires("lua/5.3.5")

        if self.options.with_thirdparty_containers:
            self.requires("robin-hood-hashing/3.9.1")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if not hasattr(self, "_cmake"):
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_LUA_BINDINGS"] = self.options.with_lua_bindings
            self._cmake.definitions["BUILD_SAMPLES"] = False
            self._cmake.definitions["CUSTOM_CONFIGURATION"] = True
            self._cmake.definitions["CUSTOM_INCLUDE_DIRS"] = ";".join(self.deps_cpp_info["robin-hood-hashing"].include_paths)
            self._cmake.definitions["DISABLE_RTTI_AND_EXCEPTIONS"] = not self.options.enable_rtti_and_exceptions
            self._cmake.definitions["ENABLE_PRECOMPILED_HEADERS"] = True
            self._cmake.definitions["ENABLE_TRACY_PROFILING"] = False
            self._cmake.definitions["MATRIX_ROW_MAJOR"] = self.options.matrix_mode == "row_major"
            self._cmake.definitions["NO_FONT_INTERFACE_DEFAULT"] = self.options.font_interface is None
            self._cmake.definitions["NO_THIRDPARTY_CONTAINERS"] = not self.options.with_thirdparty_containers

            self._cmake.configure()

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
            "FREETYPE_LIBRARIES": "Freetype_LIBRARIES",
            "LUA_FOUND": "lua_FOUND",
            "LUA_INCLUDE_DIR": "lua_INCLUDE_DIR",
            "LUA_LIBRARIES": "lua_LIBRARIES",
            # disables the built-in generation of package configuration files
            "if(PkgHelpers_AVAILABLE)": "if(FALSE)"
        }

        cmakelists_path = os.path.join(
            self._source_subfolder, "CMakeLists.txt")
        for key, value in replace_mapping.items():
            tools.replace_in_file(cmakelists_path, key, value, strict=False)

        if self.options.with_thirdparty_containers:
            config_path = os.path.join(self._source_subfolder,
                                       "Include", "RmlUi", "Config", "Config.h")
            tools.replace_in_file(
                config_path, "\"../Core/Containers/robin_hood.h\"", "<robin_hood.h>")

    def build(self):
        self._patch_sources()
        self._configure_cmake().build()

    def package(self):
        self._configure_cmake().install()
        self.copy("*LICENSE.txt", dst="licenses", src=self._source_subfolder, excludes=("Samples/*", "Tests/*"))

    def package_info(self):
        if self.options.matrix_mode == "row_major":
            self.cpp_info.defines.append("RMLUI_MATRIX_ROW_MAJOR")

        if not self.options.enable_rtti_and_exceptions:
            self.cpp_info.defines.append("RMLUI_USE_CUSTOM_RTTI")

        if not self.options.shared:
            self.cpp_info.defines.append("RMLUI_STATIC_LIB")

        if not self.options.with_thirdparty_containers:
            self.cpp_info.defines.append("RMLUI_NO_THIRDPARTY_CONTAINERS")

        if self.options.with_lua_bindings:
            self.cpp_info.libs.append("RmlLua")

        self.cpp_info.libs.append("RmlDebugger")
        self.cpp_info.libs.append("RmlCore")
