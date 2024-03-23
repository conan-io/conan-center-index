import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, VCVars

required_conan_version = ">=1.53.0"


class PremakeConan(ConanFile):
    name = "premake"
    description = (
        "Describe your software project just once, "
        "using Premake's simple and easy to read syntax, "
        "and build it everywhere"
    )
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://premake.github.io"
    topics = ("build", "build-systems")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "lto": [True, False],
    }
    default_options = {
        "lto": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os != "Windows" or is_msvc(self):
            self.options.rm_safe("lto")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler
        if self.info.settings.build_type != "Debug":
            self.info.settings.build_type = "Release"

    def requirements(self):
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("libzip/1.10.1")
        self.requires("zlib/[>=1.2.13 <2]")
        if self.version != "5.0.0-alpha15" and self.settings.os == "Linux":
            self.requires("util-linux-libuuid/2.39.2")
        # Lua sources are required during the build and cannot be unvendored

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross-building not implemented")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _conan_deps_lua(self):
        return os.path.join(self.generators_folder, "conan_paths.lua")

    def generate(self):
        if is_msvc(self):
            vcvars = VCVars(self)
            vcvars.generate()

        deps = list(reversed(self.dependencies.host.topological_sort.values()))
        deps = [dep.cpp_info.aggregated_components() for dep in deps]
        includedirs = ', '.join(f'"{p}"'.replace("\\", "/") for dep in deps for p in dep.includedirs)
        libdirs = ', '.join(f'"{p}"'.replace("\\", "/") for dep in deps for p in dep.libdirs)
        libs = ', '.join([f'"{lib}"' for dep in deps for lib in dep.libs + dep.system_libs])
        if is_apple_os(self):
            libs += ''.join(f', "{lib}.framework"' for dep in deps for lib in dep.frameworks)
        save(self, self._conan_deps_lua,
             "conan_includedirs = {%s}\nconan_libdirs = {%s}\nconan_libs = {%s}\n" %
             (includedirs, libdirs, libs))

    def _patch_sources(self):
        apply_conandata_patches(self)

        if self.options.get_safe("lto", None) is False:
            replace_in_file(self, os.path.join(self.source_folder, "premake5.lua"),
                            '"LinkTimeOptimization"', "")

        # Add missing libuuid include dir
        if self.version != "5.0.0-alpha15" and self.settings.os == "Linux":
            libuuid_info = self.dependencies["util-linux-libuuid"].cpp_info.aggregated_components()
            replace_in_file(self, os.path.join(self.source_folder, "Bootstrap.mak"),
                            " -luuid", f" -luuid -I{libuuid_info.includedirs[0]} -L{libuuid_info.libdirs[0]}")

        # Unvendor
        for lib in ["curl", "libzip", "mbedtls", "zlib"]:
            rmdir(self, os.path.join(self.source_folder, "contrib", lib))

        # Inject Conan dependencies
        replace_in_file(self, os.path.join(self.source_folder, "premake5.lua"),
                        "@CONAN_DEPS_LUA@", self._conan_deps_lua.replace("\\", "/"))

    @property
    def _os_target(self):
        return {
            "FreeBSD": "bsd",
            "Windows": "windows",
            "Linux": "linux",
            "Macos": "macosx",
        }[str(self.settings.os)]

    @property
    def _arch(self):
        return {
            "x86": "x86",
            "x86_64": "x86_64",
            "armv7": "ARM",
            "armv8": "ARM64",
        }[str(self.settings.arch)]

    def build(self):
        self._patch_sources()
        make = "nmake" if is_msvc(self) else "make"
        config = "debug" if self.settings.build_type == "Debug" else "release"
        with chdir(self, self.source_folder):
            self.run(f"{make} -f Bootstrap.mak {self._os_target} PLATFORM={self._arch} CONFIG={config}")

    def package(self):
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        suffix = ".exe" if self.settings.os == "Windows" else ""
        copy(self, f"*/premake5{suffix}",
             dst=os.path.join(self.package_folder, "bin"),
             src=os.path.join(self.source_folder, "bin"),
             keep_path=False)

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        # https://github.com/premake/premake-core/blob/v5.0.0-beta2/premake5.lua#L232-L271


        # TODO: Legacy, to be removed on Conan 2.0
        bindir = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bindir)
