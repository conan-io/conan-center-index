from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rm, rmdir
from conan.tools.microsoft import is_msvc
import os


required_conan_version = ">=2.0.9"


class OpenColladaConan(ConanFile):
    name = "opencollada"
    description = "OpenCOLLADA is a stream based reader and writer library for COLLADA files."
    license = "Khronos"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KhronosGroup/OpenCOLLADA"
    topics = ("3d", "collada", "graphics")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/*"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # OpenCOLLADA builds its own internal dependencies (zlib, pcre, libxml2)
        # from the Externals directory, so no external dependencies are needed
        pass

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def export_sources(self):
        pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["USE_STATIC"] = not self.options.shared
        tc.cache_variables["USE_SHARED"] = self.options.shared
        tc.cache_variables["BUILD_TESTING"] = False

        # OpenCOLLADA will build its own internal pcre, libxml2, and zlib from Externals

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        include = os.path.join("include", "opencollada")
        self.cpp_info.includedirs = [
            include,
            os.path.join(include, "COLLADABaseUtils"),
            os.path.join(include, "COLLADABaseUtils", "Math"),
            os.path.join(include, "COLLADAFramework"),
            os.path.join(include, "COLLADASaxFrameworkLoader"),
            os.path.join(include, "COLLADASaxFrameworkLoader", "generated14"),
            os.path.join(include, "COLLADASaxFrameworkLoader", "generated15"),
            os.path.join(include, "COLLADAStreamWriter"),
            os.path.join(include, "GeneratedSaxParser"),
        ]
        self.cpp_info.libdirs = [os.path.join("lib", "opencollada")]
        self.cpp_info.libs = [
            "OpenCOLLADABaseUtils",
            "OpenCOLLADAFramework",
            "OpenCOLLADASaxFrameworkLoader",
            "GeneratedSaxParser",
            "OpenCOLLADAStreamWriter",
            "pcre",
            "UTF",
        ]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")

        if not self.options.shared:
            self.cpp_info.defines.append("OPENCOLLADA_STATIC")
