from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
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
        "use_sse": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_sse": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.use_sse

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("expat/[>=2.6.2 <3]")
        if Version(self.version) < "2.2.0":
            self.requires("openexr/2.5.7")
        else:
            self.requires("openexr/3.2.3")
            self.requires("imath/3.1.9")

        if Version(self.version) < "2.0.0":
            self.requires("tinyxml/2.6.2")
            self.requires("yaml-cpp/0.7.0")
        else:
            self.requires("pystring/1.1.4")
            self.requires("yaml-cpp/0.8.0")

        if Version(self.version) >= "2.3.0":
            self.requires("minizip-ng/4.0.3")
        elif Version(self.version) >= "2.2.0":
            self.requires("minizip-ng/3.0.9")

        # for tools only
        self.requires("lcms/2.14")
        # TODO: add GLUT (needed for ociodisplay tool)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if Version(self.version) >= "2.3.0" and \
            self.settings.compiler == "gcc" and \
            Version(self.settings.compiler.version) < "6.0":
            raise ConanInvalidConfiguration(f"{self.ref} requires gcc >= 6.0")

        if Version(self.version) < "2.0.0" and \
            self.settings.compiler.value == "msvc" and \
            Version(self.settings.compiler.version) >= "17.0":
            raise ConanInvalidConfiguration(f"{self.ref} < 2.0 not building on MSVC 2022")

        if Version(self.version) >= "2.3.0" and \
            self.settings.compiler == "clang" and \
            self.settings.compiler.libcxx == "libc++":
            raise ConanInvalidConfiguration(f"{self.ref} deosn't support clang with libc++")

        # opencolorio>=2.2.0 requires minizip-ng with with_zlib
        if Version(self.version) >= "2.2.0" and \
            not self.dependencies["minizip-ng"].options.get_safe("with_zlib", False):
            raise ConanInvalidConfiguration(f"{self.ref} requires minizip-ng with with_zlib = True. On Apple platforms with_libcomp = False is also needed to enable the with_zlib option.")

        if Version(self.version) == "1.1.1" and self.options.shared and self.dependencies["yaml-cpp"].options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} requires static build yaml-cpp")
        if Version(self.version) >= "2.2.1" and self.options.shared and self.dependencies["minizip-ng"].options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} requires static build minizip-ng")

    def build_requirements(self):
        if Version(self.version) >= "2.2.0":
            self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_VERBOSE_MAKEFILE"] = True
        if Version(self.version) >= "2.1.0":
            tc.variables["OCIO_BUILD_PYTHON"] = False
        else:
            tc.variables["OCIO_BUILD_SHARED"] = self.options.shared
            tc.variables["OCIO_BUILD_STATIC"] = not self.options.shared
            tc.variables["OCIO_BUILD_PYGLUE"] = False

            tc.variables["USE_EXTERNAL_YAML"] = True
            tc.variables["USE_EXTERNAL_TINYXML"] = True
            tc.variables["TINYXML_OBJECT_LIB_EMBEDDED"] = False
            tc.variables["USE_EXTERNAL_LCMS"] = True

        tc.variables["OCIO_USE_SSE"] = self.options.get_safe("use_sse", False)

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

        if Version(self.version) == "1.1.1":
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenColorIO")
        self.cpp_info.set_property("cmake_target_name", "OpenColorIO::OpenColorIO")
        self.cpp_info.set_property("pkg_config_name", "OpenColorIO")

        self.cpp_info.libs = ["OpenColorIO"]

        if Version(self.version) < "2.1.0":
            if not self.options.shared:
                self.cpp_info.defines.append("OpenColorIO_STATIC")

        if is_apple_os(self):
            self.cpp_info.frameworks.extend(["Foundation", "IOKit", "ColorSync", "CoreGraphics"])
            if Version(self.version) == "2.1.0":
                self.cpp_info.frameworks.extend(["Carbon", "CoreFoundation"])

        if is_msvc(self) and not self.options.shared:
            self.cpp_info.defines.append("OpenColorIO_SKIP_IMPORTS")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenColorIO"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenColorIO"
        self.cpp_info.names["pkg_config"] = "OpenColorIO"
