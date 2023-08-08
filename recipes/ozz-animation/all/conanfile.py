import os
from pathlib import Path
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, unzip, download, replace_in_file

class OzzAnimationConan(ConanFile):
    name = "ozz-animation"
    description = "Open source c++ skeletal animation library and toolset."
    license = "MIT"
    topics = ("conan", "ozz", "animation", "skeletal")
    homepage = "https://github.com/guillaumeblanc/ozz-animation"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "gltf2ozz": [True, False],
        "ozz_geometry": [True, False],
        "ozz_animation": [True, False],
        "ozz_options": [True, False],
        "ozz_animation_offline": [True, False],
        "ozz_animation_tools": [True, False],
        #needs Autodesk FBX SDK
        #"fbx2ozz": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "gltf2ozz": False,
        "ozz_geometry": True,
        "ozz_animation": True,
        "ozz_options": False,
        "ozz_animation_offline": False,
        "ozz_animation_tools": False,
    }
    short_paths = True

    def validate(self):
        def _ensure_enabled(opt, req):
            if getattr(self.options, opt):
                missing = [r for r in req if not getattr(self.options, r, False)]
                if missing:
                    raise ConanInvalidConfiguration(f"Can't enable '{opt}' without also enabling {missing}")
        _ensure_enabled('ozz_animation_tools', ['ozz_animation_offline', 'ozz_options'])
        _ensure_enabled('ozz_animation_offline', ['ozz_animation'])

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        #this component ships an old version of jsoncpp (0.10.6) which isn't on
        #conan center, so this will prevent ODR violations until either
        #upstream updates to a newer jsoncpp version, or someone adds a package
        #for that version of jsoncpp
        if self.options.ozz_animation_tools:
            self.provides = ['jsoncpp']

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        dp = CMakeDeps(self)
        dp.generate()

    def layout(self):
        cmake_layout(self)

    def source(self):
        src = self.conan_data["sources"][self.version]
        name = src['url'].split('/')[-1]
        download(self, filename=name, **src)
        unzip(self, name, destination=self.source_folder, strip_root = True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmvars = {
            "ozz_build_fbx": False,
            "ozz_build_data": False,
            "ozz_build_samples": False,
            "ozz_build_howtos": False,
            "ozz_build_tests": False,
            "ozz_build_cpp11": True
        }
        
        if self.options.gltf2ozz:
            cmvars["ozz_build_tools"] = True
            cmvars["ozz_build_gltf"] = True

        if self.options.ozz_animation_tools:
            cmvars["ozz_build_tools"] = True

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
        cmake = self._configure_cmake()

        cmake.install()

        pkg = Path(self.package_folder)

        if self.options.ozz_animation_tools:
            json = Path(self.build_folder)/'src'/'animation'/'offline'/'tools'/'json'
            copy(self, pattern="libjson*", dst=pkg/"lib", src=str(json))

        copy(self, pattern="LICENSE.md", dst=pkg/"licenses", src=self.source_folder)

    def package_info(self):
        postfix = {
            "Debug": "_d",
            "Release": "_r",
            "MinSizeRel": "_rs",
            "RelWithDebInfo": "_rd",
        }[str(self.settings.build_type)]

        self.cpp_info.components["base"].libs = [f"ozz_base{postfix}"]
        self.cpp_info.components["base"].includedirs = ["include"]

        if self.options.ozz_geometry:
            self.cpp_info.components["geometry"].libs = [f"ozz_geometry{postfix}"]
            self.cpp_info.components["geometry"].includedirs = ["include"]
            self.cpp_info.components["geometry"].requires = ["base"]

        if self.options.ozz_animation:
            self.cpp_info.components["animation"].libs = [f"ozz_animation{postfix}"]
            self.cpp_info.components["animation"].includedirs = ["include"]
            self.cpp_info.components["animation"].requires = ["base"]

        if self.options.ozz_animation_offline:
            self.cpp_info.components["animation_offline"].libs = [f"ozz_animation_offline{postfix}"]
            self.cpp_info.components["animation_offline"].includedirs = ["include"]
            self.cpp_info.components["animation_offline"].requires = ["animation"]

        if self.options.ozz_animation_tools:
            self.cpp_info.components["jsoncpp"].libs = [f"json{postfix}"]
            self.cpp_info.components["animation_offline_tools"].libs = [f"ozz_animation_tools{postfix}"]
            self.cpp_info.components["animation_offline_tools"].includedirs = ["include"]
            self.cpp_info.components["animation_offline_tools"].requires = ["animation_offline", "options", "jsoncpp"]

        if self.options.ozz_options:
            self.cpp_info.components["options"].libs = [f"ozz_options{postfix}"]
            self.cpp_info.components["options"].includedirs = ["include"]
            self.cpp_info.components["options"].requires = ["base"]

        if self.options.gltf2ozz:
            self.buildenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin", "tools"))