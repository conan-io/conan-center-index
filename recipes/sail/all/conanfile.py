from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rename, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
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
        "with_highest_priority_codecs": [True, False],
        "with_high_priority_codecs": [True, False],
        "with_medium_priority_codecs": [True, False],
        "with_low_priority_codecs": [True, False],
        "with_lowest_priority_codecs": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "thread_safe": True,
        "with_highest_priority_codecs": True,
        "with_high_priority_codecs": True,
        "with_medium_priority_codecs": True,
        "with_low_priority_codecs": True,
        "with_lowest_priority_codecs": True,
    }
    options_description = {
        "with_highest_priority_codecs": "Enable codecs: GIF, JPEG, PNG, TIFF",
        "with_high_priority_codecs": "Enable codecs: BMP, SVG",
        "with_medium_priority_codecs": "Enable codecs: AVIF, JPEG2000, JPEGXL, WEBL",
        "with_low_priority_codecs": "Enable codecs: ICO, PCX, PNM, PSD, QOI, TGA",
        "with_lowest_priority_codecs": "Enable codecs: WAL, XBM",
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
        if self.options.with_highest_priority_codecs:
            self.requires("giflib/5.2.2")
            self.requires("libjpeg/9e")
            self.requires("libpng/[>=1.6 <2]")
            self.requires("libtiff/4.6.0")
        if self.options.with_high_priority_codecs:
            if Version(self.version) >= "0.9.1":
                self.requires("nanosvg/cci.20231025")
        if self.options.with_medium_priority_codecs:
            self.requires("libavif/1.0.4")
            self.requires("jasper/4.2.0")
            # TODO Re-enable JPEG XL after merging either of the following:
            #   - https://github.com/conan-io/conan-center-index/pull/13898
            #   - https://github.com/conan-io/conan-center-index/pull/18812
            # self.requires("libjxl/0.10.2")
            self.requires("libwebp/1.3.2")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            strip_root=True, destination=self.source_folder)

    def generate(self):
        only_codecs = []

        if self.options.with_highest_priority_codecs:
            only_codecs.append("highest-priority")
        if self.options.with_high_priority_codecs:
            only_codecs.append("high-priority")
        if self.options.with_medium_priority_codecs:
            only_codecs.append("medium-priority")
        if self.options.with_low_priority_codecs:
            only_codecs.append("low-priority")
        if self.options.with_lowest_priority_codecs:
            only_codecs.append("lowest-priority")

        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"]       = False
        tc.variables["SAIL_BUILD_APPS"]     = False
        tc.variables["SAIL_BUILD_EXAMPLES"] = False
        tc.variables["SAIL_COMBINE_CODECS"] = True
        tc.variables["SAIL_ENABLE_OPENMP"]  = False
        tc.variables["SAIL_ONLY_CODECS"]    = ";".join(only_codecs)
        # JPEGXL needs porting to Conan2
        # SVG with nanosvg is supported in >= 0.9.1
        if Version(self.version) >= "0.9.1":
            tc.variables["SAIL_DISABLE_CODECS"] = "jpegxl"
        else:
            tc.variables["SAIL_DISABLE_CODECS"] = "jpegxl;svg"
        tc.variables["SAIL_INSTALL_PDB"]    = False
        tc.variables["SAIL_THREAD_SAFE"]    = self.options.thread_safe
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

        if self.options.with_highest_priority_codecs:
            self.cpp_info.components["sail-codecs"].requires.append("giflib::giflib")
            self.cpp_info.components["sail-codecs"].requires.append("libjpeg::libjpeg")
            self.cpp_info.components["sail-codecs"].requires.append("libpng::libpng")
            self.cpp_info.components["sail-codecs"].requires.append("libtiff::libtiff")
            if Version(self.version) >= "0.9.1":
                self.cpp_info.components["sail-codecs"].requires.append("nanosvg::nanosvg")
        if self.options.with_medium_priority_codecs:
            self.cpp_info.components["sail-codecs"].requires.append("libavif::libavif")
            self.cpp_info.components["sail-codecs"].requires.append("jasper::jasper")
            # self.cpp_info.components["sail-codecs"].requires.append("libjxl::libjxl")
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
