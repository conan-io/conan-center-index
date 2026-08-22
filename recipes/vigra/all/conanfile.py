import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeDeps, CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get, export_conandata_patches, apply_conandata_patches, rm, copy, replace_in_file


class VigraConan(ConanFile):
    name = "vigra"
    description = "A generic C++ library for image analysis"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://ukoethe.github.io/vigra/"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    topics = "image-processing", "computer-vision"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_hdf5": [True, False],
        "with_openexr": [True, False],
        "with_boost_graph": [True, False],
        "with_lemon": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_hdf5": True,
        "with_openexr": True,
        "with_boost_graph": True,
        "with_lemon": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

        apply_conandata_patches(self)
        replace_in_file(
            self,
            os.path.join(self.source_folder, "src", "impex", "CMakeLists.txt"),
            'SOVERSION ${SOVERSION} INSTALL_NAME_DIR "${CMAKE_INSTALL_PREFIX}/lib${LIB_SUFFIX}"',
            'SOVERSION ${SOVERSION} INSTALL_NAME_DIR "${CMAKE_INSTALL_PREFIX}/lib${LIB_SUFFIX}" INSTALL_NAME_DIR "@rpath"'
        )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("libtiff/4.6.0")
        self.requires("libpng/[>=1.6 <2]")
        self.requires("fftw/3.3.10")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("libjpeg/9e")

        if self.options.with_hdf5:
            self.requires("hdf5/1.14.3")

        if self.options.with_openexr:
            self.requires("openexr/3.2.4")
            self.requires("imath/3.1.9")

        if self.options.with_boost_graph:
            self.requires("boost/1.85.0")

        if self.options.with_lemon:
            self.requires("coin-lemon/1.3.1")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["WITH_VIGRANUMPY"] = False
        tc.cache_variables["BUILD_DOCS"] = False
        tc.cache_variables["BUILD_TESTS"] = False

        tc.cache_variables["WITH_OPENEXR"] = self.options.with_openexr
        tc.cache_variables["WITH_BOOST_GRAPH"] = self.options.with_boost_graph
        tc.cache_variables["WITH_LEMON"] = self.options.with_lemon

        tc.cache_variables["VIGRA_STATIC_LIB"] = not self.options.shared
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cm = CMake(self)
        cm.install()
        rm(self, "*.cmake", self.package_folder, recursive=True)
        #fix_apple_shared_install_name(self)

    def package_info(self):
        if not self.options.shared:
            self.cpp_info.defines = ["VIGRA_STATIC_LIB"]

        self.cpp_info.libs = ["vigraimpex"]
        self.cpp_info.set_property("cmake_file_name", "Vigra")
        self.cpp_info.set_property("cmake_target_name", "vigraimpex")

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("shlwapi")
