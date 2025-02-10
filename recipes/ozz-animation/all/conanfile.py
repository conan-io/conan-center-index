from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, rename, get, replace_in_file, mkdir, rm, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2.0"

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
        "ozz_geometry": [True, False],
        "ozz_animation": [True, False],
        "ozz_options": [True, False],
        "ozz_animation_offline": [True, False],
        "ozz_animation_tools": [True, False],
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
    options_description = {
        "tools": "Enable gltf2ozz CLI tool",
        "ozz_geometry": "Enable runtime geometry library (skinning jobs)",
        "ozz_animation": "Enable runtime animation library",
        "ozz_options": "Enable library for parsing CLI args",
        "ozz_animation_offline": "Enable library for offline processing",
        "ozz_animation_tools": "Enable library for creating tools",
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        #this component ships an old version of jsoncpp (0.10.6) which isn't on
        #conan center, so this will prevent ODR violations until either
        #upstream updates to a newer jsoncpp version, or someone adds a package
        #for that version of jsoncpp
        if self.options.ozz_animation_tools:
            self.provides = ["jsoncpp"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

        def loose_lt_semver(v1, v2):
            return all(int(p1) < int(p2) for p1, p2 in zip(str(v1).split("."), str(v2).split(".")))

        if self.settings.compiler == "gcc" and loose_lt_semver(self.settings.compiler.version, "11.3"):
            # GCC 11.2 bug breaks build
            # https://gcc.gnu.org/bugzilla/show_bug.cgi?id=99578
            # https://github.com/guillaumeblanc/ozz-animation/issues/147
            raise ConanInvalidConfiguration("GCC 11.3 or newer required")

        if self.options.shared and Version(self.version) < "0.14.0":
            raise ConanInvalidConfiguration(f"Can't build shared library for {self.version}")

        def _ensure_enabled(opt, req):
            if self.options.get_safe(opt):
                missing = [r for r in req if not self.options.get_safe(r)]
                if missing:
                    raise ConanInvalidConfiguration(f"Option '{opt}' requires option(s) {missing} to be enabled too")
        _ensure_enabled("ozz_animation_offline", ["ozz_animation"])
        _ensure_enabled("ozz_animation_tools", ["ozz_animation_offline", "ozz_options"])
        _ensure_enabled("tools", ["ozz_animation_tools"])

    def build_requirements(self):
        if Version(self.version) >= "0.14.2":
            self.tool_requires("cmake/[>=3.24 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ozz_build_fbx"] = False
        tc.variables["ozz_build_data"] = False
        tc.variables["ozz_build_samples"] = False
        tc.variables["ozz_build_howtos"] = False
        tc.variables["ozz_build_tests"] = False
        tc.variables["ozz_build_cpp11"] = True
        tc.variables["ozz_build_tools"] = False
        tc.variables["ozz_build_gltf"] = False
        if self.options.ozz_animation_tools:
            tc.variables["ozz_build_tools"] = True
        if self.options.tools:
            tc.variables["ozz_build_tools"] = True
            tc.variables["ozz_build_gltf"] = True
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _patch_sources(self):
        if Version(self.version) < "0.14.2":
            # Removed in v0.14.3: https://github.com/guillaumeblanc/ozz-animation/commit/1db3df07173fc410d2215262f746e45f10577e32
            compiler_settings = self.source_path / "build-utils" / "cmake" / "compiler_settings.cmake"
            replace_in_file(self, compiler_settings, 'string(REGEX REPLACE "/MT" "/MD" ${flag} "${${flag}}")', "")
            replace_in_file(self, compiler_settings, 'string(REGEX REPLACE "/MD" "/MT" ${flag} "${${flag}}")', "")

        replace_in_file(self, self.source_path / "src" / "animation" / "offline" / "tools" / "CMakeLists.txt",
                        "if(NOT EMSCRIPTEN)",
                        "if(NOT CMAKE_CROSSCOMPILING)")

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, self.package_path/"licenses")
        cmake = CMake(self)
        cmake.install()

        if self.options.ozz_animation_tools:
            json_dir = self.build_path.joinpath("src", "animation", "offline", "tools", "json")
            for pattern in ["*.a", "*.so*", "*.dylib", "*.lib"]:
                copy(self, pattern, src=json_dir, dst=self.package_path/"lib", keep_path=False)
            copy(self, "*.dll", src=json_dir, dst=self.package_path/"bin", keep_path=False)

        mkdir(self, self.package_path.joinpath("bin"))
        for file in self.package_path.joinpath("lib").glob("*.dll"):
            rename(self, src=file, dst=self.package_path/"bin"/file.name)

        if self.options.tools:
            for file in self.package_path.joinpath("bin", "tools").iterdir():
                rename(self, src=file, dst=self.package_path/"bin"/file.name)
            rmdir(self, self.package_path.joinpath("bin", "tools"))

        rm(self, "*.md", self.package_path)
        rmdir(self, self.package_path / "share")

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
