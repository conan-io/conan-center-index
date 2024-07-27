import os
import re
from pathlib import Path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, load, replace_in_file
from conan.tools.google import BazelToolchain, BazelDeps, bazel_layout, Bazel
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class SkiaConan(ConanFile):
    name = "skia"
    description = ("Skia is an open source 2D graphics library which provides common APIs that work across a variety of hardware and software platforms."
                   " It serves as the graphics engine for Google Chrome and ChromeOS, Android, Flutter, and many other products.")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://skia.org/"
    topics = ("graphics", "2d", "rendering", "chromium")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        bazel_layout(self, src_folder="src", build_folder="src")

    def requirements(self):
        self.requires("dawn/cci.20240726")
        self.requires("spirv-tools/1.3.268.0")
        self.requires("spirv-cross/1.3.268.0")
        self.requires("expat/[>=2.6.2 <3]")
        self.requires("freetype/2.13.2")
        self.requires("fontconfig/2.15.0")
        self.requires("icu/75.1")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("bazel/6.2.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = BazelToolchain(self)
        tc.generate()

        deps = BazelDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Keep only the external deps that are not available from Conan
        keep_external = [
            "cxx",
            "cxxbridge_cmd",
            "fontations",
            "icu4x",
            "vello",
        ]
        for path in Path(self.source_folder, "bazel", "external").iterdir():
            if path.is_dir() and path.name not in keep_external:
                rmdir(self, path)

    def build(self):
        self._patch_sources()
        bazel = Bazel(self)
        bazel.build(target="//:skia_public")

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

        # Copy library file
        bin_dir = os.path.join(self.source_folder, "bazel-bin")
        if self.settings.os == "Windows":
            copy(self, "skia_public.lib", bin_dir, os.path.join(self.package_folder, "lib"))
        else:
            copy(self, "libskia_public.a", bin_dir, os.path.join(self.package_folder, "lib"))

        # Copy public headers based on skia_public.cppmap
        # The project examples use "include/" as the include prefix.
        # Replace this with a more appropriate "skia/" prefix, which also matches the behavior of Vcpkg and nixpkgs.
        copy(self, "SkUserConfig.h",
             os.path.join(self.source_folder, "include", "config"),
             os.path.join(self.package_folder, "include", "skia", "config"))
        cppmap = load(self, os.path.join(bin_dir, "skia_public.cppmap"))
        for m in re.finditer(r'textual header "(?:\.\./)*include/(.+)"', cppmap):
            copy(self, m.group(1),
                 os.path.join(self.source_folder, "include"),
                 os.path.join(self.package_folder, "include", "skia"))
            replace_in_file(self, os.path.join(self.package_folder, "include", "skia", m.group(1)),
                            '#include "include/', '#include "skia/', strict=False)

    def package_info(self):
        self.cpp_info.libs = ["skia_public"]
