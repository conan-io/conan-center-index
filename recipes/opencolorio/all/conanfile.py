from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.apple import is_apple_os
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class OpenColorIOConan(ConanFile):
    name = "opencolorio"
    description = "A color management framework for visual effects and animation."
    license = "BSD-3-Clause"
    homepage = "https://opencolorio.org/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("colors", "visual", "effects", "animation")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],

        # OCIO supports a number of optimized code paths using different SIMD instruction sets.
        # By default it will determin the support of the current platform. A setting of none keeps
        # those defaults, True or False will intentionally set the values.
        # OCIO_USE_SSE was an option in older versions (< 2.3.2), newer versions support the following
        # instruction sets OCIO_USE_SSE2 up to OCIO_USE_AVX512 (no pure SSE anymore).
        "use_sse": [None, True, False],
        "use_sse2": [None, True, False],
        "use_sse3": [None, True, False],
        "use_ssse3": [None, True, False],
        "use_sse4": [None, True, False],
        "use_sse42": [None, True, False],
        "use_avx": [None, True, False],
        "use_avx2": [None, True, False],
        "use_avx512": [None, True, False],
        "use_f16c": [None, True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_sse": None,
        "use_sse2": None,
        "use_sse3": None,
        "use_ssse3": None,
        "use_sse4": None,
        "use_sse42": None,
        "use_avx": None,
        "use_avx2": None,
        "use_avx512": None,
        "use_f16c": None,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        # Reproduce the previous default which was injected instead of letting it be determined
        if self.options.get_safe("use_sse", None) == None:
            self.options.use_sse = self.settings.arch in ["x86", "x86_64"]

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("expat/[>=2.6.2 <3]")
        self.requires("openexr/[>=3.3.2 <4]")
        self.requires("imath/[>=3.1.9 <4]")
        self.requires("pystring/1.1.4")
        self.requires("yaml-cpp/0.8.0")
        self.requires("minizip-ng/[>=4.0.3 <5]")

        # for tools only
        self.requires("lcms/[>=2.16 <3]")
        # TODO: add GLUT (needed for ociodisplay tool)

    def validate_build(self):
        minimum_cppstd = 11 if Version(self.version) < "2.5" else 17
        check_min_cppstd(self, minimum_cppstd)
    
    def validate(self):
        check_min_cppstd(self, 11)
        
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "6.0":
            raise ConanInvalidConfiguration(f"{self.ref} requires gcc >= 6.0")

        if self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libc++":
            raise ConanInvalidConfiguration(f"{self.ref} deosn't support clang with libc++")


    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_VERBOSE_MAKEFILE"] = True
        tc.variables["OCIO_BUILD_PYTHON"] = False

        # Selection of SIMD Instruction sets
        if not self.options.get_safe("use_sse", None) == None:
            print('Set OCIO_USE_SSE to ', self.options.use_sse)
            tc.variables["OCIO_USE_SSE"] = self.options.use_sse
        if not self.options.get_safe("use_sse2", None) == None:
            print('Set OCIO_USE_SSE2 to ', self.options.use_sse2)
            tc.variables["OCIO_USE_SSE2"] = self.options.use_sse2
        if not self.options.get_safe("use_sse3", None) == None:
            print('Set OCIO_USE_SSE3 to ', self.options.use_sse3)
            tc.variables["OCIO_USE_SSE3"] = self.options.use_sse3
        if not self.options.get_safe("use_ssse3", None) == None:
            print('Set OCIO_USE_SSSE3 to ', self.options.use_ssse3)
            tc.variables["OCIO_USE_SSSE3"] = self.options.use_ssse3
        if not self.options.get_safe("use_sse4", None) == None:
            print('Set OCIO_USE_SSE4 to ', self.options.use_sse4)
            tc.variables["OCIO_USE_SSE4"] = self.options.use_sse4
        if not self.options.get_safe("use_sse42", None) == None:
            print('Set OCIO_USE_SSE42 to ', self.options.use_sse42)
            tc.variables["OCIO_USE_SSE42"] = self.options.use_sse42
        if not self.options.get_safe("use_avx", None) == None:
            print('Set OCIO_USE_AVX to ', self.options.use_avx)
            tc.variables["OCIO_USE_AVX"] = self.options.use_avx
        if not self.options.get_safe("use_avx2", None) == None:
            print('Set OCIO_USE_AVX2 to ', self.options.use_avx2)
            tc.variables["OCIO_USE_AVX2"] = self.options.use_avx2
        if not self.options.get_safe("use_avx512", None) == None:
            print('Set OCIO_USE_AVX512 to ', self.options.use_avx512)
            tc.variables["OCIO_USE_AVX512"] = self.options.use_avx512
        if not self.options.get_safe("use_f16c", None) == None:
            print('Set OCIO_USE_F16C to ', self.options.use_f16c)
            tc.variables["OCIO_USE_F16C"] = self.options.use_f16c

        # openexr 2.x provides Half library
        tc.variables["OCIO_USE_OPENEXR_HALF"] = True

        tc.variables["OCIO_BUILD_APPS"] = True
        tc.variables["OCIO_BUILD_DOCS"] = False
        tc.variables["OCIO_BUILD_TESTS"] = False
        tc.variables["OCIO_BUILD_GPU_TESTS"] = False
        tc.variables["OCIO_USE_BOOST_PTR"] = False

        # avoid downloading dependencies
        tc.variables["OCIO_INSTALL_EXT_PACKAGE"] = "NONE"

        if is_msvc(self) and not self.options.shared:
            # define any value because ifndef is used
            tc.variables["OpenColorIO_SKIP_IMPORTS"] = True

        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0091"] = "NEW"

        if self.settings.os == "Linux":
            # Workaround for: https://github.com/conan-io/conan/issues/13560
            libdirs_host = [l for dependency in self.dependencies.host.values() for l in dependency.cpp_info.aggregated_components().libdirs]
            tc.variables["CMAKE_BUILD_RPATH"] = ";".join(libdirs_host)

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        for module in ("expat", "lcms2", "pystring", "yaml-cpp", "Imath", "minizip-ng"):
            rm(self, "Find"+module+".cmake", os.path.join(self.source_folder, "share", "cmake", "modules"))

    def build(self):
        self._patch_sources()

        cm = CMake(self)
        cm.configure()
        cm.build()

    def package(self):
        cm = CMake(self)
        cm.install()

        if not self.options.shared:
            copy(self, "*",
                src=os.path.join(self.package_folder, "lib", "static"),
                dst=os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "static"))

        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        # nop for 2.x
        rm(self, "OpenColorIOConfig*.cmake", self.package_folder)
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenColorIO")
        self.cpp_info.set_property("cmake_target_name", "OpenColorIO::OpenColorIO")
        self.cpp_info.set_property("pkg_config_name", "OpenColorIO")

        self.cpp_info.libs = ["OpenColorIO"]

        if is_apple_os(self):
            self.cpp_info.frameworks.extend(["Foundation", "IOKit", "ColorSync", "CoreGraphics"])

        if is_msvc(self) and not self.options.shared:
            self.cpp_info.defines.append("OpenColorIO_SKIP_IMPORTS")
