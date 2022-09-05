from conan import ConanFile
from conan.tools.scm import Version
from conan.tools import files
from conan.errors import ConanInvalidConfiguration
from conans import AutoToolsBuildEnvironment, CMake

import os
import functools

required_conan_version = ">=1.47.0"

class MoldConan(ConanFile):
    name = "mold"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rui314/mold/"
    license = "AGPL-3.0"
    description = ("mold is a faster drop-in replacement for existing Unix linkers. It is several times faster than the LLVM lld linker")
    topics = ("mold", "ld", "linkage", "compilation")

    settings = "os", "arch", "compiler", "build_type"

    generators = "make", "cmake", "cmake_find_package"

    def validate(self):
        if self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration('Mold is a build tool, specify mold:build_type=Release in your build profile, see https://github.com/conan-io/conan-center-index/pull/11536#issuecomment-1195607330')
        if self.settings.compiler in ["gcc", "clang", "intel-cc"] and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration('Mold can only be built with libstdc++11; specify mold:compiler.libcxx=libstdc++11 in your build profile')
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f'{self.name} can not be built on {self.settings.os}.')
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "10":
            raise ConanInvalidConfiguration("GCC version 10 or higher required")
        if (self.settings.compiler == "clang" or self.settings.compiler == "apple-clang") and Version(self.settings.compiler.version) < "12":
            raise ConanInvalidConfiguration("Clang version 12 or higher required")
        if self.settings.compiler == "apple-clang" and "armv8" == self.settings.arch :
            raise ConanInvalidConfiguration(f'{self.name} is still not supported by Mac M1.')

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        if Version(self.version) > "1.4.0":
            self.copy("CMakeLists.txt")

    def _get_include_path(self, dependency):
        include_path = self.deps_cpp_info[dependency].rootpath
        include_path = os.path.join(include_path, "include")
        return include_path

    def _patch_sources(self):
        if self.settings.compiler == "apple-clang" or (self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "11"):
            files.replace_in_file(self, "source_subfolder/Makefile", "-std=c++20", "-std=c++2a")

        files.replace_in_file(self, "source_subfolder/Makefile", "-Ithird-party/xxhash ", "-I{} -I{} -I{} -I{} -I{}".format(
        self._get_include_path("zlib"),
        self._get_include_path("openssl"),
        self._get_include_path("xxhash"),
        self._get_include_path("mimalloc"),
        self._get_include_path("onetbb")
        ))

        files.replace_in_file(self, "source_subfolder/Makefile", "MOLD_LDFLAGS += -ltbb", "MOLD_LDFLAGS += -L{} -ltbb".format(
            self.deps_cpp_info["onetbb"].lib_paths[0]))

        files.replace_in_file(self, "source_subfolder/Makefile", "MOLD_LDFLAGS += -lmimalloc", "MOLD_LDFLAGS += -L{} -lmimalloc".format(
            self.deps_cpp_info["mimalloc"].lib_paths[0]))

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["MOLD_USE_SYSTEM_MIMALLOC"] = True
        cmake.definitions["MOLD_USE_SYSTEM_TBB"] = True
        cmake.definitions["MOLD_USE_MOLD"] = False
        cmake.configure()
        return cmake

    def build_requirements(self):
        self.tool_requires("cmake/3.23.0")

    def requirements(self):
        self.requires("zlib/1.2.12")
        self.requires("openssl/1.1.1q")
        self.requires("onetbb/2021.3.0")
        self.requires("mimalloc/2.0.6")
        self.requires("xxhash/0.8.1")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        if Version(self.version) < "1.4":
            self._patch_sources()
            with files.chdir(self, self._source_subfolder):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.make(target="mold", args=['SYSTEM_TBB=1', 'SYSTEM_MIMALLOC=1'])
        else:
            # Error out if ZLIB is not found, we want to be predictable
            files.replace_in_file(self, "source_subfolder/CMakeLists.txt", "find_package(ZLIB QUIET)", "find_package(ZLIB REQUIRED)")
            # Since we introduce a conan wrapper, CMAKE_SOURCE_DIR points to a dir above. mold_SOURD_DIR is an equivalent to the intended behavior
            files.replace_in_file(self, "source_subfolder/CMakeLists.txt", "${CMAKE_SOURCE_DIR}/update-git-hash.py", "${mold_SOURCE_DIR}/update-git-hash.py")
            # This is a bug upstream. You can't assing definitions to a target you don't build. It has been addressed on main but not released.
            files.replace_in_file(self, "source_subfolder/CMakeLists.txt", "target_compile_definitions(mimalloc INTERFACE USE_SYSTEM_MIMALLOC)", "target_compile_definitions(mold PRIVATE USE_SYSTEM_MIMALLOC)")
            # Use conan's xxhash
            files.replace_in_file(self, "source_subfolder/CMakeLists.txt", "target_link_libraries(mold PRIVATE ${CMAKE_DL_LIBS})", "target_link_libraries(mold PRIVATE ${CMAKE_DL_LIBS})\nfind_package(xxHash REQUIRED)\ntarget_link_libraries(xxHash::xxhash)")
            files.replace_in_file(self, "source_subfolder/mold.h", '#include "third-party/xxhash/xxhash.h"', '#include "xxhash.h"')

            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        if Version(self.version) < "1.4":
            self.copy("mold", src=self._source_subfolder, dst="bin", keep_path=False)
        else:
            cmake = self._configure_cmake()
            cmake.install()
            files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_id(self):
        del self.info.settings.compiler

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
