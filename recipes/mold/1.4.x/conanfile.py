import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, get
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version

class MoldConan(ConanFile):
    name = "mold"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rui314/mold/"
    license = "AGPL-3.0"
    description = ("mold is a faster drop-in replacement for existing Unix linkers. It is several times faster than the LLVM lld linker")
    topics = ("mold", "ld", "linkage", "compilation")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_mimalloc": [True, False],
    }
    default_options = {
        "with_mimalloc": False,
    }
    generators = "cmake_find_package"

    def validate(self):
        if self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration('Mold is a build tool, specify mold:build_type=Release in your build profile, see https://github.com/conan-io/conan-center-index/pull/11536#issuecomment-1195607330')
        if self.settings.compiler in ["gcc", "clang", "intel-cc"] and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration('Mold can only be built with libstdc++11; specify mold:compiler.libcxx=libstdc++11 in your build profile')
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "10":
            raise ConanInvalidConfiguration("GCC version 10 or higher required")
        if self.settings.compiler in ('clang', 'apple-clang') and Version(self.settings.compiler.version) < "12":
            raise ConanInvalidConfiguration("Clang version 12 or higher required")
        if self.settings.compiler == "apple-clang" and "armv8" == self.settings.arch :
            raise ConanInvalidConfiguration(f'{self.name} is still not supported by Mac M1.')

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/3.24.1")

    def requirements(self):
        self.requires("zlib/1.2.12")
        self.requires("openssl/1.1.1q")
        self.requires("xxhash/0.8.1")
        self.requires("onetbb/2021.3.0")
        if self.options.with_mimalloc:
            self.requires("mimalloc/2.0.6")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MOLD_USE_MIMALLOC"] = self.options.with_mimalloc
        tc.variables["MOLD_USE_SYSTEM_MIMALLOC"] = True
        tc.variables["MOLD_USE_SYSTEM_TBB"] = True
        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        
    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        mold_location = os.path.join(bindir, "bindir")

        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)
        self.env_info.LD = mold_location
        self.buildenv_info.prepend_path("MOLD_ROOT", bindir)
        self.cpp_info.includedirs = []

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
