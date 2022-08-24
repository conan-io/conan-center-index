from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.45.0"


class DetoursConan(ConanFile):
    name = "detours"
    homepage = "https://github.com/antlr/antlr4/tree/master/runtime/Cpp"
    description = "Detours is a software package for monitoring and instrumenting API calls on Windows"
    topics = ("monitoror", "instrumenting", "hook", "injection")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Only os=Windows is supported")
        # if not is_msvc(self):
        #     raise ConanInvalidConfiguration("Only the MSVC compiler is supported")
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
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    @property
    def _target_processor(self):
        return {
            "x86": "X86",
            "x86_64": "X64",
            "armv7": "ARM",
            "armv8": "ARM64",
        }[str(self.settings.arch)]

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def _patch_sources(self):
        if is_msvc(self):
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "src", "Makefile"),
                                  "/MT ", f"/{self.settings.compiler.runtime} ")

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            with tools.vcvars(self):
                with tools.files.chdir(self, os.path.join(self._source_subfolder, "src")):
                    self.run(f"nmake DETOURS_TARGET_PROCESSOR={self._target_processor}")
        else:
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")
        if is_msvc(self):
            self.copy("detours.lib", src=os.path.join(self._source_subfolder, f"lib.{self._target_processor}"), dst="lib")
            self.copy("*.h", src=os.path.join(self._source_subfolder, "include"), dst="include")
        else:
            cmake = CMake(self)
            cmake.install()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libs = ["detours"]
        if self.settings.compiler == "gcc":
            self.cpp_info.system_libs = [tools.stdcpp_library(self)]
            self.cpp_info.link_flags = ["-static-libgcc", "-static-libstdc++"]
