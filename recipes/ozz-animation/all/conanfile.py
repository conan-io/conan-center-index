import os
from pathlib import Path
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, rename, get, replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"

class OzzAnimationConan(ConanFile):
    name = "ozz-animation"
    description = "Open source c++ skeletal animation library and toolset."
    license = "MIT"
    topics = ("ozz", "animation", "skeletal")
    homepage = "https://github.com/guillaumeblanc/ozz-animation"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],

        #runtime geometry library (skinning jobs)
        "ozz_geometry": [True, False],

        #runtime animation library
        "ozz_animation": [True, False],

        #library for parsing CLI args
        "ozz_options": [True, False],

        #library for offline processing
        "ozz_animation_offline": [True, False],

        #library for creating tools
        "ozz_animation_tools": [True, False],

        #gltf2ozz CLI tool
        "tools": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "tools": False,
        "ozz_geometry": True,
        "ozz_animation": True,
        "ozz_options": False,
        "ozz_animation_offline": False,
        "ozz_animation_tools": False,
    }

    def validate(self):
        def _ensure_enabled(opt, req):
            if self.options.get_safe(opt):
                missing = [r for r in req if not getattr(self.options, r, False)]
                if missing:
                    raise ConanInvalidConfiguration(f"Option '{opt}' requires option(s) {missing} to be enabled too")
        _ensure_enabled('ozz_animation_offline', ['ozz_animation'])
        _ensure_enabled('ozz_animation_tools', ['ozz_animation_offline', 'ozz_options'])
        _ensure_enabled('tools', ['ozz_animation_tools'])

        if self.settings.compiler == 'gcc':
            # GCC 11.2 bug breaks build
            # https://gcc.gnu.org/bugzilla/show_bug.cgi?id=99578
            # https://github.com/guillaumeblanc/ozz-animation/issues/147
            if Version(self.settings.compiler.version) < "11.3":
                raise ConanInvalidConfiguration(f"GCC 11.3 or newer required")

        if self.options.shared and Version(self.version) < "0.14.0":
            raise ConanInvalidConfiguration(f"Can't build shared library for {self.version}")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        #this component ships an old version of jsoncpp (0.10.6) which isn't on
        #conan center, so this will prevent ODR violations until either
        #upstream updates to a newer jsoncpp version, or someone adds a package
        #for that version of jsoncpp
        if self.options.ozz_animation_tools:
            self.provides = ['jsoncpp']

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmvars = {
            "ozz_build_fbx": False,
            "ozz_build_data": False,
            "ozz_build_samples": False,
            "ozz_build_howtos": False,
            "ozz_build_tests": False,
            "ozz_build_cpp11": True,
            "ozz_build_tools": False,
            "ozz_build_gltf": False,
        }
        
        if self.options.ozz_animation_tools:
            cmvars["ozz_build_tools"] = True

        if self.options.tools:
            cmvars["ozz_build_tools"] = True
            cmvars["ozz_build_gltf"] = True

        cmake.configure(variables = cmvars)
        return cmake

    def build(self):
        subfolder = Path(self.source_folder)
        for before, after in [('string(REGEX REPLACE "/MT" "/MD" ${flag} "${${flag}}")', ""), ('string(REGEX REPLACE "/MD" "/MT" ${flag} "${${flag}}")', "")]:
            replace_in_file(self, subfolder/"build-utils"/"cmake"/"compiler_settings.cmake", before, after)

        replace_in_file(self, subfolder/"src"/"animation"/"offline"/"tools"/"CMakeLists.txt",
                              "if(NOT EMSCRIPTEN)",
                              "if(NOT CMAKE_CROSSCOMPILING)")

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        pkg = self.package_path

        if self.options.ozz_animation_tools:
            json = Path(self.build_folder)/'src'/'animation'/'offline'/'tools'/'json'
            copy(self, "*.a", src=json, dst=pkg/'lib', keep_path=False)
            copy(self, "*.so", src=json, dst=pkg/'lib', keep_path=False)
            copy(self, "*.dylib", src=json, dst=pkg/'lib', keep_path=False)
            copy(self, "*.lib", src=json, dst=pkg/'lib', keep_path=False)
            copy(self, "*.dll", src=json, dst=pkg/'bin', keep_path=False)

        os.remove(pkg/"CHANGES.md")
        os.remove(pkg/"LICENSE.md")
        os.remove(pkg/"README.md")

        (pkg/'bin').mkdir(exist_ok=True)
        for file in filter(lambda p: p.suffix=='.dll', (pkg/'lib').iterdir()):
            rename(self, src=file, dst=pkg/'bin'/file.name)

        copy(self, pattern="LICENSE.md", dst=pkg/"licenses", src=self.source_folder)

    def package_info(self):
        postfix = {
            "Debug": "_d",
            "Release": "_r",
            "MinSizeRel": "_rs",
            "RelWithDebInfo": "_rd",
        }[str(self.settings.build_type)]

        def _add_libm(c):
            if self.settings.os in ("Linux", "Android", "FreeBSD"):
                self.cpp_info.components[c].system_libs = ["m"]

        self.cpp_info.components["base"].libs = [f"ozz_base{postfix}"]
        _add_libm("base")

        if self.options.ozz_geometry:
            self.cpp_info.components["geometry"].libs = [f"ozz_geometry{postfix}"]
            self.cpp_info.components["geometry"].requires = ["base"]
            _add_libm("geometry")

        if self.options.ozz_animation:
            self.cpp_info.components["animation"].libs = [f"ozz_animation{postfix}"]
            self.cpp_info.components["animation"].requires = ["base"]
            _add_libm("animation")

        if self.options.ozz_animation_offline:
            self.cpp_info.components["animation_offline"].libs = [f"ozz_animation_offline{postfix}"]
            self.cpp_info.components["animation_offline"].requires = ["animation"]
            _add_libm("animation_offline")

        if self.options.ozz_options:
            self.cpp_info.components["options"].libs = [f"ozz_options{postfix}"]
            self.cpp_info.components["options"].requires = ["base"]
            _add_libm("options")

        if self.options.ozz_animation_tools:
            self.cpp_info.components["animation_tools"].libs = [f"ozz_animation_tools{postfix}"]
            self.cpp_info.components["animation_tools"].requires = ["animation_offline", "options", "jsoncpp"]
            self.cpp_info.components["jsoncpp"].libs = [f"json{postfix}"]

        if self.options.tools:
            self.buildenv_info.prepend_path("PATH", str(Path(self.package_folder)/"bin"/"tools"))
