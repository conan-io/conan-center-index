from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rename, rmdir
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"

class SAILConan(ConanFile):
    name = "sail"
    description = "The missing small and fast image decoding library for humans (not for machines)"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sail.software"
    topics = ( "image", "encoding", "decoding", "graphics" )
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "thread_safe": [True, False],
        "with_avif": [True, False],
        "with_gif": [True, False],
        "with_jpeg2000": [True, False],
        "with_jpeg": ["libjpeg", "libjpeg-turbo", False],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_webp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "thread_safe": True,
        "with_avif": True,
        "with_gif": True,
        "with_jpeg2000": True,
        "with_jpeg": "libjpeg",
        "with_png": True,
        "with_tiff": True,
        "with_webp": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        if self.options.with_avif:
            self.requires("libavif/0.11.1")
        if self.options.with_gif:
            self.requires("giflib/5.2.1")
        if self.options.with_jpeg2000:
            self.requires("jasper/4.0.0")
        if self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.5")
        elif self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        if self.options.with_png:
            self.requires("libpng/1.6.40")
        if self.options.with_tiff:
            self.requires("libtiff/4.5.1")
        if self.options.with_webp:
            self.requires("libwebp/1.3.1")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            strip_root=True, destination=self.source_folder)

    def generate(self):
        enable_codecs = []

        if self.options.with_avif:
            enable_codecs.append("avif")
        if self.options.with_gif:
            enable_codecs.append("gif")
        if self.options.with_jpeg2000:
            enable_codecs.append("jpeg2000")
        if self.options.with_jpeg:
            enable_codecs.append("jpeg")
        if self.options.with_png:
            enable_codecs.append("png")
        if self.options.with_tiff:
            enable_codecs.append("tiff")
        if self.options.with_webp:
            enable_codecs.append("webp")

        tc = CMakeToolchain(self)
        tc.variables["SAIL_BUILD_APPS"] = False
        tc.variables["SAIL_BUILD_EXAMPLES"] = False
        tc.variables["SAIL_BUILD_TESTS"] = False
        tc.variables["SAIL_COMBINE_CODECS"] = True
        tc.variables["SAIL_ENABLE_CODECS"] = ";".join(enable_codecs)
        tc.variables["SAIL_INSTALL_PDB"] = False
        tc.variables["SAIL_THREAD_SAFE"] = self.options.thread_safe
        # TODO: Remove after fixing https://github.com/conan-io/conan/issues/12012
        if is_msvc(self):
            tc.cache_variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = str(self.settings.build_type)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",       self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE.INIH.txt",  self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE.MUNIT.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))

        cmake = CMake(self)
        cmake.install()

        # Remove CMake and pkg-config rules
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # Move icons
        rename(self, os.path.join(self.package_folder, "share"),
                     os.path.join(self.package_folder, "res"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Sail")

        self.cpp_info.filenames["cmake_find_package"]       = "Sail"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Sail"
        self.cpp_info.names["cmake_find_package"]           = "SAIL"
        self.cpp_info.names["cmake_find_package_multi"]     = "SAIL"

        self.cpp_info.components["sail-common"].set_property("cmake_target_name", "SAIL::SailCommon")
        self.cpp_info.components["sail-common"].set_property("pkg_config_name", "libsail-common")
        self.cpp_info.components["sail-common"].names["cmake_find_package"]       = "SailCommon"
        self.cpp_info.components["sail-common"].names["cmake_find_package_multi"] = "SailCommon"
        self.cpp_info.components["sail-common"].includedirs = ["include/sail"]
        self.cpp_info.components["sail-common"].libs = ["sail-common"]

        self.cpp_info.components["sail-codecs"].set_property("cmake_target_name", "SAIL::SailCodecs")
        self.cpp_info.components["sail-codecs"].names["cmake_find_package"]       = "SailCodecs"
        self.cpp_info.components["sail-codecs"].names["cmake_find_package_multi"] = "SailCodecs"
        self.cpp_info.components["sail-codecs"].libs = ["sail-codecs"]
        self.cpp_info.components["sail-codecs"].requires = ["sail-common"]
        if self.options.with_avif:
            self.cpp_info.components["sail-codecs"].requires.append("libavif::libavif")
        if self.options.with_gif:
            self.cpp_info.components["sail-codecs"].requires.append("giflib::giflib")
        if self.options.with_jpeg2000:
            self.cpp_info.components["sail-codecs"].requires.append("jasper::jasper")
        if self.options.with_jpeg:
            self.cpp_info.components["sail-codecs"].requires.append("{0}::{0}".format(self.options.with_jpeg))
        if self.options.with_png:
            self.cpp_info.components["sail-codecs"].requires.append("libpng::libpng")
        if self.options.with_tiff:
            self.cpp_info.components["sail-codecs"].requires.append("libtiff::libtiff")
        if self.options.with_webp:
            self.cpp_info.components["sail-codecs"].requires.append("libwebp::libwebp")

        self.cpp_info.components["libsail"].set_property("cmake_target_name", "SAIL::Sail")
        self.cpp_info.components["libsail"].set_property("pkg_config_name", "libsail")
        self.cpp_info.components["libsail"].names["cmake_find_package"] = "Sail"
        self.cpp_info.components["libsail"].names["cmake_find_package_multi"] = "Sail"
        self.cpp_info.components["libsail"].libs = ["sail"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libsail"].system_libs.append("dl")
            if self.options.thread_safe:
                self.cpp_info.components["libsail"].system_libs.append("pthread")
        self.cpp_info.components["libsail"].requires = ["sail-common", "sail-codecs"]

        self.cpp_info.components["sail-manip"].set_property("cmake_target_name", "SAIL::SailManip")
        self.cpp_info.components["sail-manip"].set_property("pkg_config_name", "libsail-manip")
        self.cpp_info.components["sail-manip"].names["cmake_find_package"]       = "SailManip"
        self.cpp_info.components["sail-manip"].names["cmake_find_package_multi"] = "SailManip"
        self.cpp_info.components["sail-manip"].libs = ["sail-manip"]
        self.cpp_info.components["sail-manip"].requires = ["sail-common"]

        self.cpp_info.components["sail-c++"].set_property("cmake_target_name", "SAIL::SailC++")
        self.cpp_info.components["sail-c++"].set_property("pkg_config_name", "libsail-c++")
        self.cpp_info.components["sail-c++"].names["cmake_find_package"]       = "SailC++"
        self.cpp_info.components["sail-c++"].names["cmake_find_package_multi"] = "SailC++"
        self.cpp_info.components["sail-c++"].libs = ["sail-c++"]
        self.cpp_info.components["sail-c++"].requires = ["libsail", "sail-manip"]
