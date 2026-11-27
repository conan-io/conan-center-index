import io
import json
import os
import re

from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, load, save

required_conan_version = ">=2.0.9"


class HobbesConan(ConanFile):
    name = "hobbes"
    description = "A language and an embedded JIT compiler for dynamic expression evaluation, data storage and analysis"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/morganstanley/hobbes"
    topics = ("jit", "compiler", "llvm", "language", "structured-logging")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
        # one terminal library in hi, not two: readline's default here is
        # termcap, which defines the same symbols as the ncurses it also needs
        "readline/*:with_library": "curses",
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # hobbes's headers include LLVM's (hobbes/util/llvm.H), so its users compile against them too
        self.requires("llvm-core/19.1.7", transitive_headers=True)
        self.requires("zlib/[>=1.2.11 <2]")
        # For hi's prompt only (and with it, the ncurses that readline draws
        # the terminal with). It is linked into hi and not into the library,
        # so a user of the package neither sees nor links it.
        self.requires("readline/8.2", visible=False)

    def validate(self):
        check_min_cppstd(self, 17)
        if self.settings.os not in ("Linux", "Macos"):
            raise ConanInvalidConfiguration("hobbes builds on Linux and macOS only")
        if self.settings.arch not in ("x86_64", "armv8"):
            raise ConanInvalidConfiguration("hobbes generates code for x86-64 and AArch64 only")
        if self.dependencies["llvm-core"].options.shared:
            raise ConanInvalidConfiguration("hobbes links LLVM statically (llvm-core:shared=False)")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.19 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        # hobbes asks llvm-config which libraries to link and gets them by name
        # (-lLLVMCore ... -lz3 -lxml2 ...), so the linker has to be told where
        # the packages that hold them are
        libdirs = []
        for dep in self.dependencies.host.values():
            libdirs.extend(dep.cpp_info.aggregated_components().libdirs)
        link_dirs = ["-L" + d for d in libdirs]
        tc.extra_exelinkflags.extend(link_dirs)
        tc.extra_sharedlinkflags.extend(link_dirs)
        # find_package(Readline) is answered by the package's own CMake config
        # here, not by hobbes's cmake/FindReadline.cmake, and that doesn't set
        # the variables CMakeLists.txt reads; set them, to the package's target
        readline = self.dependencies["readline"].cpp_info.aggregated_components()
        tc.cache_variables["Readline_INCLUDE_DIRS"] = ";".join(readline.includedirs)
        tc.cache_variables["Readline_LIBRARIES"] = "readline::readline"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        # not the default target, which is also the test suite
        cmake.build(target="hobbes-pic" if self.options.fPIC else "hobbes")
        cmake.build(target="hi")
        cmake.build(target="hog")

    def _llvm_config(self, *args):
        """Ask the llvm-config that CMakeLists.txt found (and linked hobbes by) a question."""
        cache = load(self, os.path.join(self.build_folder, "CMakeCache.txt"))
        found = re.search(r"^llvm-config:FILEPATH=(.+)$", cache, re.MULTILINE)
        if not found or found.group(1).endswith("-NOTFOUND"):
            raise ConanException("can't tell which llvm-config hobbes was built with")
        out = io.StringIO()
        self.run('"%s" %s' % (found.group(1), " ".join(args)), stdout=out)
        return out.getvalue().split()

    def _llvm_libs(self):
        """The LLVM libraries a program that links this package needs.

        That is the libraries of the components hobbes uses, not all of LLVM
        (which would bring in, for one, the line editor and the terminal
        library under it). llvm-config knows which those are, so it is asked
        now -- the same llvm-config, for the same components, as
        CMakeLists.txt -- and the answer is kept with the package.
        """
        components = ["ipo", "aarch64" if self.settings.arch == "armv8" else "x86", "mcjit", "orcjit"]
        libs = self._llvm_config("--libs", "--link-static", *components)
        return [l[2:] for l in libs if l.startswith("-l")]

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "NOTICE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.H", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
        lib = "libhobbes-pic.a" if self.options.fPIC else "libhobbes.a"
        copy(self, lib, self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        for tool in ("hi", "hog"):
            copy(self, tool, self.build_folder, os.path.join(self.package_folder, "bin"), keep_path=False)
        save(self, os.path.join(self.package_folder, "lib", "hobbes-llvm.json"),
             json.dumps({"libs": self._llvm_libs()}, indent=2))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "hobbes")
        self.cpp_info.set_property("cmake_target_name", "hobbes::hobbes")
        self.cpp_info.libs = ["hobbes-pic" if self.options.fPIC else "hobbes"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread", "dl", "rt"]
        llvm = json.loads(load(self, os.path.join(self.package_folder, "lib", "hobbes-llvm.json")))
        # (each LLVM library is a component of the llvm-core package)
        self.cpp_info.requires = ["zlib::zlib"] + ["llvm-core::" + lib for lib in llvm["libs"]]
