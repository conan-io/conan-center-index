import os

from conan import ConanFile
from conan.tools.files import get, copy, apply_conandata_patches, export_conandata_patches, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime

required_conan_version = ">=2.4"


class MsdfAtlasGenConan(ConanFile):
    name = "msdf-atlas-gen"
    description = "MSDF font atlas generator"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Chlumsky/msdf-atlas-gen"
    topics = ("msdf-atlas-gen", "msdf", "font", "atlas")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    implements = ["auto_shared_fpic"]
    languages = "C++"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)

    def requirements(self):
        self.requires("msdfgen/1.13", transitive_headers=True)
        self.requires("artery-font-format/1.1")
        self.requires("libpng/[>=1.6 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["MSDF_ATLAS_BUILD_STANDALONE"] = True
        tc.cache_variables["MSDF_ATLAS_USE_VCPKG"] = False
        tc.cache_variables["MSDF_ATLAS_USE_SKIA"] = False
        tc.cache_variables["MSDF_ATLAS_NO_ARTERY_FONT"] = False
        tc.cache_variables["MSDF_ATLAS_MSDFGEN_EXTERNAL"] = True
        tc.cache_variables["MSDF_ATLAS_INSTALL"] = True
        tc.cache_variables["MSDF_ATLAS_DYNAMIC_RUNTIME"] = not is_msvc_static_runtime(self)
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.preprocessor_definitions["MSDFGEN_USE_LIBPNG"] = 1
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.components["msdf-atlas-gen"].set_property("cmake_target_name", "msdf-atlas-gen::msdf-atlas-gen")
        self.cpp_info.components["msdf-atlas-gen"].libs = ["msdf-atlas-gen"]
        self.cpp_info.components["msdf-atlas-gen"].defines.append("MSDF_ATLAS_STANDALONE")
        self.cpp_info.components["msdf-atlas-gen"].requires = ["msdfgen::msdfgen",
                                                               "artery-font-format::artery-font-format",
                                                               "libpng::libpng"]
        if is_msvc(self):
            self.cpp_info.components["msdf-atlas-gen"].defines.append("MSDF_ATLAS_PUBLIC=__declspec(dllimport)"
                                                                        if self.options.shared else "MSDF_ATLAS_PUBLIC=")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["msdf-atlas-gen"].system_libs = ["pthread"]

        self.cpp_info.components["msdf-atlas-gen-run"].set_property("cmake_target_name", "msdf-atlas-gen::msdf-atlas-gen-run")
        self.cpp_info.components["msdf-atlas-gen-run"].set_property("cmake_target_aliases", ["msdf-atlas-gen-standalone::msdf-atlas-gen-standalone"])
        self.cpp_info.components["msdf-atlas-gen-run"].exe = "msdf-atlas-gen"
        self.cpp_info.components["msdf-atlas-gen-run"].location = os.path.join("bin", "msdf-atlas-gen")
        self.cpp_info.components["msdf-atlas-gen-run"].requires = ["msdf-atlas-gen", "msdfgen::msdfgen",
                                                                  "artery-font-format::artery-font-format",
                                                                  "libpng::libpng"]
