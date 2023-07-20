import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import chdir, copy, get, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.47.0"


class MoldConan(ConanFile):
    name = "mold"
    description = (
        "mold is a faster drop-in replacement for existing Unix linkers. "
        "It is several times faster than the LLVM lld linker."
    )
    license = "AGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rui314/mold/"
    topics = ("ld", "linkage", "compilation")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("xxhash/0.8.2")
        self.requires("onetbb/2021.10.0")
        self.requires("mimalloc/2.1.2")

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration(
                "Mold is a build tool, specify mold/*:build_type=Release in your build profile, see"
                " https://github.com/conan-io/conan-center-index/pull/11536#issuecomment-1195607330"
            )
        if self.settings.compiler in ["gcc", "clang", "intel-cc"] and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration(
                "Mold can only be built with libstdc++11;"
                " specify mold:compiler.libcxx=libstdc++11 in your build profile"
            )
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.name} can not be built on {self.settings.os}.")
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "10":
            raise ConanInvalidConfiguration("GCC version 10 or higher required")
        if (self.settings.compiler == "clang" or self.settings.compiler == "apple-clang") and Version(
            self.settings.compiler.version
        ) < "12":
            raise ConanInvalidConfiguration("Clang version 12 or higher required")
        if self.settings.compiler == "apple-clang" and "armv8" == self.settings.arch:
            raise ConanInvalidConfiguration(f"{self.name} is still not supported by Mac M1.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _get_include_path(self, dependency):
        include_path = self.dependencies[dependency].package_folder
        include_path = os.path.join(include_path, "include")
        return include_path

    def _patch_sources(self):
        makefile_path = os.path.join(self.source_folder, "Makefile")
        if self.settings.compiler == "apple-clang" or (
            self.settings.compiler == "gcc" and
            Version(self.settings.compiler.version) < "11"
        ):
            replace_in_file(self, makefile_path, "-std=c++20", "-std=c++2a")
        replace_in_file(self, makefile_path,
            "-Ithird-party/xxhash ",
            " ".join(
                "-I{}".format(self._get_include_path(dep))
                for dep in ["zlib", "openssl", "xxhash", "mimalloc", "onetbb"]
            ),
        )
        replace_in_file(self, makefile_path,
            "MOLD_LDFLAGS += -ltbb",
            "MOLD_LDFLAGS += -L{} -ltbb".format(self.dependencies["onetbb"].cpp_info.libdirs[0]),
        )
        replace_in_file(self, makefile_path,
            "MOLD_LDFLAGS += -lmimalloc",
            "MOLD_LDFLAGS += -L{} -lmimalloc".format(self.dependencies["mimalloc"].cpp_info.libdirs[0]),
        )

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.make_args = ["SYSTEM_TBB=1", "SYSTEM_MIMALLOC=1"]
        tc.generate()

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make(target="mold")

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "mold",
             src=os.path.join(self.source_folder, "bin"),
             dst=os.path.join(self.package_folder, "bin"),
             keep_path=False)
        copy(self, "mold",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "bin"),
            keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread", "dl"]

        bindir = os.path.join(self.package_folder, "bin")
        mold_executable = os.path.join(bindir, "mold")
        self.conf_info.define("user.mold:mold", mold_executable)
        self.buildenv_info.define_path("MOLD_ROOT", bindir)
        self.buildenv_info.define("LD", mold_executable)

        # For legacy Conan 1.x consumers only:
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)
        self.env_info.MOLD_ROOT = bindir
        self.env_info.LD = mold_executable
