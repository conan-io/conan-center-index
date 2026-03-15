import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy, export_conandata_patches, apply_conandata_patches

required_conan_version = ">=2"


class BemanUtfViewConan(ConanFile):
    name = "beman-utf_view"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bemanproject/utf_view"
    license = "Apache-2.0"
    package_type = "library"
    description = "C++29 UTF Transcoding Views"
    topics = ("algorithm", "ranges")
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "header_only": [True, False],
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "header_only": True,
        "shared": False,
        "fPIC": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, "23")

    def layout(self):
        if self.options.header_only:
            basic_layout(self)
        else:
            cmake_layout(self)

    def requirements(self):
        self.requires("beman-transform_view/[<1]", transitive_headers=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only:
            self.options.rm_safe("fPIC")
            self.options.rm_safe("shared")
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not self.options.header_only:
            deps = CMakeDeps(self)
            deps.generate()

            tc = CMakeToolchain(self)
            tc.variables["BEMAN_UTF_VIEW_BUILD_TESTS"] = False
            tc.variables["BEMAN_UTF_VIEW_BUILD_EXAMPLES"] = False
            tc.variables["BEMAN_UTF_VIEW_BUILD_PAPER"] = False
            tc.variables["BEMAN_UTF_VIEW_INSTALL_CONFIG_FILE_PACKAGE"] = False
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        if self.options.header_only:
            copy(self, "*", dst=os.path.join(self.package_folder, "include"),
                 src=os.path.join(self.source_folder, "include"))
        else:
            cmake = CMake(self)
            cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "beman.utf_view")
        self.cpp_info.set_property("pkg_config_name", "beman.utf_view")
        self.cpp_info.set_property("cmake_target_name", "beman::utf_view")

        if self.options.header_only:
            self.cpp_info.bindirs = []
            self.cpp_info.libdirs = []
        else:
            self.cpp_info.libs = ["beman.utf_view"]

        self.cpp_info.requires = ["beman-transform_view::beman-transform_view"]
