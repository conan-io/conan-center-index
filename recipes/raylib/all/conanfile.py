from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save, replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.54.0"


class RaylibConan(ConanFile):
    name = "raylib"
    description = "raylib is a simple and easy-to-use library to enjoy videogames programming."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.raylib.com/"
    topics = ("gamedev",)
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "opengl_version": [None, "4.3", "3.3", "2.1", "1.1", "ES-2.0"],

        "module_rshapes": [True, False],
        "module_rtextures": [True, False],
        "module_rtext": [True, False],
        "module_rmodels": [True, False],
        "module_raudio": [True, False],

        "mouse_gestures": [True, False],
        "default_font": [True, False],
        "screen_capture": [True, False],
        "gif_recording": [True, False],
        "busy_wait_loop": [True, False],
        "events_waiting": [True, False],
        "compression_api": [True, False],
        "events_automation": [True, False],
        "custom_frame_control": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "opengl_version": None,

        "module_rshapes": True,
        "module_rtextures": True,
        "module_rtext": True,
        "module_rmodels": True,
        "module_raudio": True,

        "mouse_gestures": True,
        "default_font": True,
        "screen_capture": True,
        "gif_recording": True,
        "busy_wait_loop": False,
        "events_waiting": False,
        "compression_api": True,
        "events_automation": False,
        "custom_frame_control": False
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os == "Android":
            del self.options.opengl_version

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os not in ["Android", "Emscripten"]:
            self.requires("glfw/3.4")
            self.requires("opengl/system")
        if self.settings.os == "Linux":
            self.requires("xorg/system")

    def validate(self):
        if self.options.module_rtext and not self.options.module_rtextures:
            raise ConanInvalidConfiguration('-o="raylib/*:module_rtext=True" needs -o="raylib/*:module_rtextures=True"')

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXAMPLES"] = False
        if self.settings.os == "Emscripten":
            tc.variables["PLATFORM"] = "Web"
            tc.variables["USE_EXTERNAL_GLFW"] = "ON"
            tc.variables["OPENGL_VERSION"] = "ES 2.0"
        if self.settings.os == "Android":
            tc.variables["PLATFORM"] = "Android"
            tc.variables["USE_EXTERNAL_GLFW"] = "OFF"
            tc.variables["OPENGL_VERSION"] = "ES 2.0"
        else:
            tc.variables["USE_EXTERNAL_GLFW"] = "ON"
            tc.variables["OPENGL_VERSION"] = "OFF" if not self.options.opengl_version else self.options.opengl_version
        tc.variables["WITH_PIC"] = self.options.get_safe("fPIC", True)

        tc.variables["CUSTOMIZE_BUILD"] = True
        true_false = lambda x: True if x else False
        tc.variables["SUPPORT_MODULE_RSHAPES"]   = true_false(self.options.module_rshapes)
        tc.variables["SUPPORT_MODULE_RTEXTURES"] = true_false(self.options.module_rtextures)
        tc.variables["SUPPORT_MODULE_RTEXT"]     = true_false(self.options.module_rtext)
        tc.variables["SUPPORT_MODULE_RMODELS"]   = true_false(self.options.module_rmodels)
        tc.variables["SUPPORT_MODULE_RAUDIO"]    = true_false(self.options.module_raudio)

        # this makes it include the headers rcamera.h, rgesture.h and rprand.h
        tc.variables["SUPPORT_CAMERA_SYSTEM"] = True
        tc.variables["SUPPORT_GESTURES_SYSTEM"] = True
        tc.variables["SUPPORT_RPRAND_GENERATOR"] = True

        tc.variables["SUPPORT_MOUSE_GESTURES"] = true_false(self.options.mouse_gestures)
        tc.variables["SUPPORT_DEFAULT_FONT"] = true_false(self.options.default_font)
        tc.variables["SUPPORT_SCREEN_CAPTURE"] = true_false(self.options.screen_capture)
        tc.variables["SUPPORT_GIF_RECORDING"] = true_false(self.options.gif_recording)
        tc.variables["SUPPORT_BUSY_WAIT_LOOP"] = true_false(self.options.busy_wait_loop)
        tc.variables["SUPPORT_EVENTS_WAITING"] = true_false(self.options.events_waiting)
        tc.variables["SUPPORT_COMPRESSION_API"] = true_false(self.options.compression_api)
        tc.variables["SUPPORT_EVENTS_AUTOMATION"] = true_false(self.options.events_automation)
        tc.variables["SUPPORT_CUSTOM_FRAME_CONTROL"] = true_false(self.options.custom_frame_control)

        # Due to a specific logic of cmakedeps_macros.cmake used by CMakeDeps to try to locate shared libs on Windows
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0054"] = "NEW"

        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"raylib": "raylib::raylib"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "raylib")
        self.cpp_info.set_property("cmake_target_name", "raylib")
        self.cpp_info.set_property("pkg_config_name", "raylib")
        libname = "raylib"
        if is_msvc(self) and not self.options.shared and Version(self.version) < "4.0.0":
            libname += "_static"
        self.cpp_info.libs = [libname]
        if is_msvc(self) and self.options.shared:
            self.cpp_info.defines.append("USE_LIBTYPE_SHARED")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("winmm")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
