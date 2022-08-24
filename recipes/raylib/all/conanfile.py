from conan import ConanFile, tools
from conans import CMake
import os
import textwrap

required_conan_version = ">=1.43.0"


class RaylibConan(ConanFile):
    name = "raylib"
    description = "raylib is a simple and easy-to-use library to enjoy videogames programming."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.raylib.com/"
    topics = ("raylib", "gamedev")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_external_glfw": [True, False],
        "opengl_version":[None, "3.3","2.1","1.1","ES-2.0"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_external_glfw": True,
        "opengl_version" : None
    }

    exports_sources = ["CMakeLists.txt","patches/**"]
    generators = "cmake", "cmake_find_package_multi"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        
        if self.options.use_external_glfw and self.settings.os != "Android":
            self.requires("glfw/3.3.6")
        
        if self.settings.os != "Android":
            self.requires("opengl/system")
        
        if self.settings.os == "Linux":
            self.requires("xorg/system")
 
    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)



    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_EXAMPLES"] = False

        if self.settings.os == "Android":
            self._cmake.definitions["PLATFORM"] = "Android"
            self._cmake.definitions["USE_EXTERNAL_GLFW"] = "OFF"
            self._cmake.definitions["OPENGL_VERSION"] = "ES 2.0"
        else:
            self._cmake.definitions["USE_EXTERNAL_GLFW"] = "OFF" if self.options.use_external_glfw else "ON"
            self._cmake.definitions["OPENGL_VERSION"] = "OFF" if not self.options.opengl_version  else self.options.opengl_version
        
        self._cmake.definitions["WITH_PIC"] = self.options.get_safe("fPIC", True)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
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
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "raylib")
        self.cpp_info.set_property("cmake_target_name", "raylib")
        self.cpp_info.set_property("pkg_config_name", "raylib")
        libname = "raylib"
        if self._is_msvc and not self.options.shared and self.version == '3.5.0':
            libname += "_static"
        self.cpp_info.libs = [libname]
        if self._is_msvc and self.options.shared:
            self.cpp_info.defines.append("USE_LIBTYPE_SHARED")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("winmm")

        self.cpp_info.builddirs.append(self._module_subfolder)
        
        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
