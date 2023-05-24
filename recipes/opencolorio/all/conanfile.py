from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get, apply_conandata_patches, export_conandata_patches, rmdir, copy, rm
from conan.tools.build import check_min_cppstd
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
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

    generators = "CMakeDeps"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.use_sse

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("expat/2.4.8")
        self.requires("openexr/2.5.7")
        self.requires("yaml-cpp/0.7.0")
        if tools.Version(self.version) < "2.0.0":
            self.requires("tinyxml/2.6.2")
        else:
            self.requires("pystring/1.1.3")
        # for tools only
        self.requires("lcms/2.13.1")
        # TODO: add GLUT (needed for ociodisplay tool)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        if Version(self.version) >= "2.1.0":
            tc.cache_variables["OCIO_BUILD_PYTHON"] = False
        else:
            tc.cache_variables["OCIO_BUILD_SHARED"] = self.options.shared
            tc.cache_variables["OCIO_BUILD_STATIC"] = not self.options.shared
            tc.cache_variables["OCIO_BUILD_PYGLUE"] = False

            tc.cache_variables["USE_EXTERNAL_YAML"] = True
            tc.cache_variables["USE_EXTERNAL_TINYXML"] = True
            tc.cache_variables["USE_EXTERNAL_LCMS"] = True

        tc.cache_variables["OCIO_USE_SSE"] = self.options.get_safe("use_sse", False)

        # openexr 2.x provides Half library
        tc.cache_variables["OCIO_USE_OPENEXR_HALF"] = True

        tc.cache_variables["OCIO_BUILD_APPS"] = True
        tc.cache_variables["OCIO_BUILD_DOCS"] = False
        tc.cache_variables["OCIO_BUILD_TESTS"] = False
        tc.cache_variables["OCIO_BUILD_GPU_TESTS"] = False
        tc.cache_variables["OCIO_USE_BOOST_PTR"] = False

        # avoid downloading dependencies
        tc.cache_variables["OCIO_INSTALL_EXT_PACKAGE"] = "NONE"

        if is_msvc(self) and not self.options.shared:
            # define any value because ifndef is used
            tc.cache_variables["OpenColorIO_SKIP_IMPORTS"] = True

        tc.generate()

    def build(self):
        apply_conandata_patches(self)

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        if not self.options.shared:
            copy(self, "*", src=os.path.join(self.package_folder, "lib", "static"), dst="lib")
            rmdir(self, os.path.join(self.package_folder, "lib", "static"))

        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        # nop for 2.x
        rm(self, "OpenColorIOConfig*.cmake", self.package_folder, recursive=True)

        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"), recursive=True)

        copy(self, "LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenColorIO")
        self.cpp_info.set_property("cmake_target_name", "OpenColorIO::OpenColorIO")
        self.cpp_info.set_property("pkg_config_name", "OpenColorIO")

        self.cpp_info.libs = ["OpenColorIO"]

        if tools.Version(self.version) < "2.1.0":
            if not self.options.shared:
                self.cpp_info.defines.append("OpenColorIO_STATIC")

        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["Foundation", "IOKit", "ColorSync", "CoreGraphics"])

        if is_msvc(self) and not self.options.shared:
            self.cpp_info.defines.append("OpenColorIO_SKIP_IMPORTS")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenColorIO"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenColorIO"
        self.cpp_info.names["pkg_config"] = "OpenColorIO"
