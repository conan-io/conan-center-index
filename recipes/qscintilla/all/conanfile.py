import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get

required_conan_version = ">=2.0.5"


class QScintillaConan(ConanFile):
    name = "qscintilla"
    description = "QScintilla is a Qt port of the Scintilla text editing component"
    license = "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://riverbankcomputing.com/software/qscintilla"
    topics = ("qt", "scintilla", "text-editor", "widget")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["qt"].widgets = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("qt/[>=6.7.1 <7]", transitive_headers=True, transitive_libs=True, run=can_run(self))

    def validate(self):
        check_min_cppstd(self, 11)
        if not self.dependencies["qt"].options.widgets:
            raise ConanInvalidConfiguration("QScintilla requires -o qt/*:widgets=True")

    def build_requirements(self):
        if not can_run(self):
            self.tool_requires("qt/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["QSCINTILLA_BUILD_DESIGNER_PLUGIN"] = self.dependencies["qt"].options.qttools
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        qt_major = self.dependencies["qt"].ref.version.major
        lib_name = f"qscintilla2_qt{qt_major}"
        if self.settings.build_type == "Debug":
            if is_apple_os(self):
                lib_name += "_debug"
            elif self.settings.os == "Windows":
                lib_name += "d"
        if not self.options.shared:
            lib_name += "_static"
        self.cpp_info.libs = [lib_name]

        self.cpp_info.requires = ["qt::qtWidgets"]
        if self.settings.os != "iOS":
            self.cpp_info.requires.append("qt::qtPrintSupport")
        if qt_major == 5 and is_apple_os(self):
            self.cpp_info.frameworks.extend(["qtMacExtras"])
