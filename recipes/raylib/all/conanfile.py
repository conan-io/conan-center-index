from conans import ConanFile, CMake, tools
import os
import textwrap

required_conan_version = ">=1.33.0"


class RaylibConan(ConanFile):
    name = "raylib"
    description = "raylib is a simple and easy-to-use library to enjoy videogames programming."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.raylib.com/"
    topics = ("conan", "raylib", "gamedev")

    settings = "os", "arch", "compiler", "build_type"
    options = { "shared": [True, False], "fPIC": [True, False] }
    default_options = { "shared": False, "fPIC": True }

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package_multi"
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("glfw/3.3.3")
        self.requires("opengl/system")
        if self.settings.os == "Linux":
            self.requires("xorg/system")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        # avoid symbols conflicts with Win SDK
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "core.c"),
                              "#define GLFW_EXPOSE_NATIVE_WIN32", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["WITH_PIC"] = self.options.get_safe("fPIC", True)
        self._cmake.definitions["USE_EXTERNAL_GLFW"] = "ON"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_subfolder, self._module_file),
            {"raylib": "raylib::raylib"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return "conan-official-{}-targets.cmake".format(self.name)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "raylib"
        self.cpp_info.names["cmake_find_package_multi"] = "raylib"
        self.cpp_info.names["pkg_config"] = "raylib"
        self.cpp_info.builddirs.append(self._module_subfolder)
        module_rel_path = os.path.join(self._module_subfolder, self._module_file)
        self.cpp_info.build_modules["cmake_find_package"] = [module_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [module_rel_path]
        libname = "raylib"
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            libname += "_static"
        self.cpp_info.libs = [libname]
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            self.cpp_info.defines.append("USE_LIBTYPE_SHARED")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("winmm")
