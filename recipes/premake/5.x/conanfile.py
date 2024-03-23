import glob
import os
import re
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, replace_in_file, rmdir, load, save
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, MSBuildToolchain, is_msvc, check_min_vs

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

    def requirements(self):
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("libzip/1.10.1")
        self.requires("mbedtls/3.5.2")
        self.requires("zlib/1.3.1")
        if self.settings.os != "Windows":
            self.requires("util-linux-libuuid/2.39.2")
        # Lua sources are required during the build and cannot be unvendored

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross-building not implemented")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _ide_version(self):
        compiler_version = str(self.settings.compiler.version)
        if str(self.settings.compiler) == "Visual Studio":
            return {"17": "2022",
                    "16": "2019",
                    "15": "2017",
                    "14": "2015",
                    "12": "2013"}.get(compiler_version)
        else:
            return {"193": "2022",
                    "192": "2019",
                    "191": "2017",
                    "190": "2015",
                    "180": "2013"}.get(compiler_version)

    @property
    def _msvc_build_dir(self):
        return os.path.join(self.source_folder, "build", f"vs{self._ide_version}")

    @property
    def _gmake_platform(self):
        return {
            "FreeBSD": "bsd",
            "Windows": "windows",
            "Linux": "unix",
            "Macos": "macosx",
        }[str(self.settings.os)]

    @property
    def _gmake_build_dir(self):
        return os.path.join(self.source_folder, "build", f"gmake2.{self._gmake_platform}")

    @property
    def _gmake_config(self):
        build_type = "debug" if self.settings.build_type == "Debug" else "release"
        if self.settings.os == "Windows":
            arch = {
                "x86": "x86",
                "x86_64": "x64",
            }[str(self.settings.arch)]
            config = f"{build_type}_{arch}"
        else:
            config = build_type
        return config

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.make_args = ["verbose=1", f"config={self._gmake_config}"]
            tc.generate()
            deps = AutotoolsDeps(self)
            deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if self.options.get_safe("lto", None) is False:
            for fn in glob.glob(os.path.join(self._gmake_build_dir, "*.make")):
                replace_in_file(self, fn, "-flto", "", strict=False)
        if check_min_vs(self, 193, raise_invalid=False):
            # Create VS 2022 project directory based on VS 2019 one
            if "alpha" in str(self.version):
                shutil.move(os.path.join(self.source_folder, "build", "vs2019"),
                            os.path.join(self.source_folder, "build", "vs2022"))
                for vcxproj in glob.glob(os.path.join(self.source_folder, "build", "vs2022", "*.vcxproj")):
                    replace_in_file(self, vcxproj, "v142", "v143")

        # Unvendor
        for lib in ["curl", "libzip", "mbedtls", "zlib"]:
            rmdir(self, os.path.join(self.source_folder, "contrib", lib))
        replace_in_file(self, os.path.join(self._gmake_build_dir, "Makefile"),
                        "contrib: curl-lib lua-lib luashim-lib mbedtls-lib zip-lib zlib-lib",
                        "contrib: lua-lib luashim-lib")
        replace_in_file(self, os.path.join(self._gmake_build_dir, "Makefile"),
                        "Premake5: lua-lib zip-lib zlib-lib curl-lib mbedtls-lib",
                        "Premake5: lua-lib")
        content = load(self, os.path.join(self._gmake_build_dir, "Premake5.make"))
        # bin/Release/liblua-lib.a -> -llua
        content = re.sub(r"\bbin/(?:Release|Debug)/lib(\w+)-lib.a\b",
                         lambda m: f"-l{m[1]}" if m[1] != "lua" else m[0], content)
        content = re.sub(r" -I../../contrib/(\S+)",
                         lambda m: "" if "lua" not in m[1] else m[0], content)
        content = content.replace(" $(LDDEPS)", "")
        content = content.replace("-lzlib", "-lz")
        save(self, os.path.join(self._gmake_build_dir, "Premake5.make"), content)

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            with chdir(self, self._msvc_build_dir):
                msbuild = MSBuild(self)
                msbuild.build(sln="Premake5.sln")
        else:
            with chdir(self, self._gmake_build_dir):
                autotools = Autotools(self)
                autotools.make(target="Premake5")

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

        # TODO: Legacy, to be removed on Conan 2.0
        bindir = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bindir)
