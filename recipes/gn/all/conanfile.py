import os
import textwrap

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import chdir, copy, get, load, save, replace_in_file, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, VCVars

required_conan_version = ">=2.1"


class GnConan(ConanFile):
    name = "gn"
    description = "GN is a meta-build system that generates build files for Ninja."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gn.googlesource.com/"
    topics = ("build system", "ninja")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def export_sources(self):
        export_conandata_patches(self)
    
    def validate_build(self):
        check_min_cppstd(self, 20)

    def build_requirements(self):
        self.tool_requires("ninja/[>=1.11.1 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version])
        apply_conandata_patches(self)

        # if compiler is not defined via Conan config (e.g. CXX buildenv flag, or compiler config),
        # default to `c++` executable, which is the system default on most systems
        replace_in_file(self, os.path.join(self.source_folder, "build/gen.py"), "'clang++'", "'c++'")

        # support windows arm64
        replace_in_file(self, os.path.join(self.source_folder, "src", "util", "build_config.h"),
                        "defined(__aarch64__)", "defined(__aarch64__) || defined(_M_ARM64)")

    def generate(self):

        if is_msvc(self):
            vcvars = VCVars(self)
            vcvars.generate()
        else:
            # gen.py listens to CXX, LD, CFLAGS, CXXFLAGS, which are defined by AutotoolsToolchain,
            # this handles compiler (if other than default) and cross-compilation flags (e.g. macOS)
            tc = AutotoolsToolchain(self)
            tc.generate()

        if self.settings.os == "Windows":
            gn_platform = "msvc"
        elif self.settings.os == "Macos":
            gn_platform = "darwin"
        else:
            # may not work, best guess
            gn_platform = str(self.settings.os).lower()
        
        configure_args = [
            "--no-last-commit-position",
            f"--host={gn_platform}",
        ]
        if self.settings.build_type in ["Debug", "RelWithDebInfo"]:
            configure_args.append("-d")
        save(self, os.path.join(self.source_folder, "configure_args"), " ".join(configure_args))

    def build(self):
        with chdir(self, self.source_folder):
            # Generate dummy header to be able to run `build/gen.py` with `--no-last-commit-position`.
            # This allows running the script without the tree having to be a git checkout.
            save(self, os.path.join(self.source_folder, "src", "gn", "last_commit_position.h"),
                textwrap.dedent("""\
                    #pragma once
                    #define LAST_COMMIT_POSITION "1"
                    #define LAST_COMMIT_POSITION_NUM 1
                    """),
            )

            build_gen_py = os.path.join(self.source_folder, "build/gen.py")

            # Disable GenerateLastCommitPosition()
            replace_in_file(self, build_gen_py,
                            "def GenerateLastCommitPosition(host, header):",
                            "def GenerateLastCommitPosition(host, header):\n  return")
            
            if is_msvc(self):
                if self.settings.build_type not in ["Debug", "RelWithDebInfo"]:
                    replace_in_file(self, build_gen_py, "'/DEBUG', ", "")
                    replace_in_file(self, build_gen_py, "'/MACHINE:x64', ", "")

            python = "python" if self.settings_build.os == "Windows" else "python3"
            self.run(f"{python} build/gen.py " + load(self, "configure_args"))
            build_jobs = self.conf.get("tools.build:jobs", default=os.cpu_count())
            verbose = "-v" if self.conf.get("tools.compilation:verbosity") == "verbose" else ""
            self.run(f"ninja -C out -j{build_jobs} {verbose}")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        gn_bin = "gn.exe" if self.settings.os == "Windows" else "gn"
        copy(self, gn_bin, src=os.path.join(self.source_folder, "out"), dst=os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
