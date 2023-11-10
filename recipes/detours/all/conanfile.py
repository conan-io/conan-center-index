import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import chdir, copy, get, replace_in_file
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, msvc_runtime_flag, VCVars

required_conan_version = ">=1.53.0"


class DetoursConan(ConanFile):
    name = "detours"
    description = "Detours is a software package for monitoring and instrumenting API calls on Windows"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/microsoft/Detours"
    topics = ("monitoring", "instrumenting", "hook", "injection", "windows")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _target_processor(self):
        return {
            "x86": "X86",
            "x86_64": "X64",
            "armv7": "ARM",
            "armv8": "ARM64",
        }[str(self.settings.arch)]

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Only os=Windows is supported")
        if is_msvc(self) and not is_msvc_static_runtime(self):
            # Debug and/or dynamic runtime is undesired for a hooking library
            raise ConanInvalidConfiguration("Only static runtime is supported (MT)")
        if self.settings.build_type != "Release":
            raise ConanInvalidConfiguration("Detours only supports the Release build type")
        try:
            self.output.info(f"target process is {self._target_processor}")
        except KeyError:
            raise ConanInvalidConfiguration("Unsupported architecture")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            vcvars = VCVars(self)
            vcvars.generate()
        else:
            tc = CMakeToolchain(self)
            tc.generate()

    def _patch_sources(self):
        if is_msvc(self):
            replace_in_file(
                self,
                os.path.join(self.source_folder, "src", "Makefile"),
                "/MT ",
                f"/{msvc_runtime_flag(self)} ",
            )

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            with chdir(self, os.path.join(self.source_folder, "src")):
                self.run(f"nmake DETOURS_TARGET_PROCESSOR={self._target_processor}")
        else:
            cmake = CMake(self)
            cmake.configure(build_script_folder=self.source_path.parent)
            cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            copy(self, "detours.lib",
                src=os.path.join(self.source_folder, f"lib.{self._target_processor}"),
                dst=os.path.join(self.package_folder, "lib"))
            copy(self, "*.h",
                src=os.path.join(self.source_folder, "include"),
                dst=os.path.join(self.package_folder, "include"))
        else:
            cmake = CMake(self)
            cmake.install()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.libs = ["detours"]
        if self.settings.compiler == "gcc":
            self.cpp_info.system_libs = [stdcpp_library(self)]
            self.cpp_info.link_flags = ["-static-libgcc", "-static-libstdc++"]
