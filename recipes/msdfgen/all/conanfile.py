from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class MsdfgenConan(ConanFile):
    name = "msdfgen"
    description = "Multi-channel signed distance field generator"
    license = "MIT"
    topics = ("msdf", "shape", "glyph", "font")
    homepage = "https://github.com/Chlumsky/msdfgen"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openmp": [True, False],
        "with_skia": [True, False],
        "utility": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openmp": False,
        "with_skia": False,
        "utility": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("freetype/2.12.1")
        if  Version(self.version) < "1.10":
            self.requires("lodepng/cci.20200615")
        else:
            self.requires("libpng/1.6.39")
        self.requires("tinyxml2/9.0.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} shared not supported by Visual Studio")
        if self.options.with_skia:
            raise ConanInvalidConfiguration("skia recipe not available yet in CCI")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MSDFGEN_BUILD_MSDFGEN_STANDALONE"] = self.options.utility
        tc.variables["MSDFGEN_USE_OPENMP"] = self.options.with_openmp
        tc.variables["MSDFGEN_USE_CPP11"] = True
        tc.variables["MSDFGEN_USE_SKIA"] = self.options.with_skia
        tc.variables["MSDFGEN_INSTALL"] = True
        if Version(self.version) >= "1.10":
            tc.variables["MSDFGEN_DYNAMIC_RUNTIME"] = not is_msvc_static_runtime(self)
            tc.variables["MSDFGEN_USE_VCPKG"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        # workaround against CMAKE_FIND_PACKAGE_PREFER_CONFIG ON in conan toolchain
        replace_in_file(self, cmakelists, "find_package(Freetype REQUIRED)", "find_package(Freetype REQUIRED MODULE)")
        # remove bundled lodepng & tinyxml2
        rmdir(self, os.path.join(self.source_folder, "lib"))
        rmdir(self, os.path.join(self.source_folder, "include"))
        # very weird but required for Visual Studio when libs are unvendored (at least for Ninja generator)
        if is_msvc(self):
            if Version(self.version) < "1.10":
                replace_in_file(
                    self,
                    cmakelists,
                    "set_target_properties(msdfgen-standalone PROPERTIES ARCHIVE_OUTPUT_DIRECTORY archive OUTPUT_NAME msdfgen)",
                    "set_target_properties(msdfgen-standalone PROPERTIES OUTPUT_NAME msdfgen IMPORT_PREFIX foo)",
                )
            else:
                replace_in_file(
                    self,
                    cmakelists,
                    'set_property(TARGET msdfgen-core PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")',
                    ''
                )
                replace_in_file(
                    self,
                    cmakelists,
                    'set_property(TARGET msdfgen-ext PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")',
                    ''
                )
                replace_in_file(
                    self,
                    cmakelists,
                    'set_property(TARGET msdfgen PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")',
                    ''
                )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "msdfgen")
        # Required to avoid some side effect in CMakeDeps generator of downstream recipes
        self.cpp_info.set_property("cmake_target_name", "msdfgen::msdgen-all-unofficial")

        self.cpp_info.names["cmake_find_package"] = "msdfgen"
        self.cpp_info.names["cmake_find_package_multi"] = "msdfgen"

        includedir = os.path.join("include", "msdfgen")

        self.cpp_info.components["_msdfgen"].set_property("cmake_target_name", "msdfgen::msdfgen")
        self.cpp_info.components["_msdfgen"].names["cmake_find_package"] = "msdfgen"
        self.cpp_info.components["_msdfgen"].names["cmake_find_package_multi"] = "msdfgen"
        self.cpp_info.components["_msdfgen"].includedirs.append(includedir)
        self.cpp_info.components["_msdfgen"].libs = ["msdfgen" if Version(self.version) < "1.10" else "msdfgen-core"]
        self.cpp_info.components["_msdfgen"].defines = ["MSDFGEN_USE_CPP11"]
        if Version(self.version) >= "1.10":
            if self.options.shared and is_msvc(self):
                self.cpp_info.components["_msdfgen"].defines.append("MSDFGEN_PUBLIC=__declspec(dllimport)")
            else:
                self.cpp_info.components["_msdfgen"].defines.append("MSDFGEN_PUBLIC=")

        self.cpp_info.components["msdfgen-ext"].set_property("cmake_target_name", "msdfgen::msdfgen-ext")
        self.cpp_info.components["msdfgen-ext"].names["cmake_find_package"] = "msdfgen-ext"
        self.cpp_info.components["msdfgen-ext"].names["cmake_find_package_multi"] = "msdfgen-ext"
        self.cpp_info.components["msdfgen-ext"].includedirs.append(includedir)
        self.cpp_info.components["msdfgen-ext"].libs = ["msdfgen-ext"]
        self.cpp_info.components["msdfgen-ext"].requires = [
            "_msdfgen", "freetype::freetype",
            "lodepng::lodepng" if Version(self.version) < "1.10" else "libpng::libpng",
            "tinyxml2::tinyxml2",
        ]

        if self.options.with_skia:
            self.cpp_info.components["msdfgen-ext"].defines.append("MSDFGEN_USE_SKIA")

        if self.options.utility:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
