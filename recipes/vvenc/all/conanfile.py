import os
import sys

from conan import ConanFile, conan_version
# FIXME: linter complains, but function is there
# https://docs.conan.io/2.0/reference/tools/build.html?highlight=check_min_cppstd#conan-tools-build-check-max-cppstd
# from conan.tools.build import stdcpp_library, check_min_cppstd, check_max_cppstd
from conan.tools.build import stdcpp_library, check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rmdir, rm
from conan.tools.scm import Version

required_conan_version = ">=1.60.1"


class vvencRecipe(ConanFile):
    name = "vvenc"
    description = "Fraunhofer Versatile Video Encoder (VVenC)"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.hhi.fraunhofer.de/en/departments/vca/technologies-and-solutions/h266-vvc.html"
    topics = ("video", "encoder", "codec", "vvc", "h266")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def validate_build(self):
        if conan_version.major == 2:
            self._validate_build2()
        elif conan_version.major == 1:
            self._validate_build1()

    def _validate_build1(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 14)
        # compiler.cppstd isn't set! but we still continue here in V1,
        # imagining just like compiler.cppstd was set to 14
        # while package_id doesn't reflect that at all, and cppstd_default also
        # might be different from 14, we silently force -std=c++14 to be
        # specified during the build. it may produce more incompatibilities,
        # and break user's expectation
        # (like, output binary depends really on C++14 symbols libstdc++.so)
        # it's V1 design flaw which isn't going to be addressed here
        # (and probably nowhere, because conan V1 is going to be discontinued in CCI)
        # once V1 is retired, that code will be removed altogether
        self.output.warning("compiler.cppstd is not set, but we assume C++14")

    def _validate_build2(self):
        # validates the minimum and maximum C++ standard supported
        # currently, the project can only be built with C++14 standard
        # it cannot be built with older standard because
        # it doesn't have all the C++ features needed
        # and it cannot be built with newer C++ standard
        # because they have existing C++ features removed
        check_min_cppstd(self, 14)
        if Version(self.version) < "1.10.0":
            # FIXME: linter complains, but function is there
            # https://docs.conan.io/2.0/reference/tools/build.html?highlight=check_min_cppstd#conan-tools-build-check-max-cppstd
            check_max_cppstd = getattr(sys.modules['conan.tools.build'], 'check_max_cppstd')
            check_max_cppstd(self, 14)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe('fPIC')

    def layout(self):
        cmake_layout(self, src_folder='src')

    def package_id(self):
        # still important, older binutils cannot recognize
        # object files created with newer binutils,
        # thus linker cannot find any valid object and therefore symbols
        # (fails to find `vvenc_get_version`, which is obviously always there)
        # this is not exactly modeled by conan right now,
        # so "compiler" setting is closest thing to avoid an issue
        # (while technically it's not a compiler, but linker and archiver)
        # del self.info.settings.compiler
        pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["VVENC_ENABLE_LINK_TIME_OPT"] = False
        tc.cache_variables["VVENC_ENABLE_LINK_TIME_OPT"] = False
        if self.settings.compiler in ["gcc", 'clang']:
            tc.blocks["cmake_flags_init"].template += '\nstring(APPEND CMAKE_C_FLAGS_INIT " -Wno-uninitialized")'
            tc.blocks["cmake_flags_init"].template += '\nstring(APPEND CMAKE_CXX_FLAGS_INIT " -Wno-uninitialized")'
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", 'pkgconfig'))
        rmdir(self, os.path.join(self.package_folder, 'lib', "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, 'bin'))
        rm(self, '*.pdb', os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["vvenc"]
        if self.options.shared:
            self.cpp_info.defines.extend(["VVENC_DYN_LINK"])  # vvcencDecl.h
        libcxx = stdcpp_library(self)  # source code is C++, but interface is pure C
        libcxx = [libcxx] if libcxx else []
        libm = ["m"] if self.settings.get_safe("os") == "Linux" else []
        libpthread = ['pthread'] if self.settings.get_safe('os') == 'Linux' else []
        self.cpp_info.system_libs.extend(libcxx + libm + libpthread)
