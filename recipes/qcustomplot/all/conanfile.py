from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, export_conandata_patches, replace_in_file
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class QCustomPlotConan(ConanFile):
    name = "qcustomplot"
    description = "QCustomPlot is a Qt C++ widget for plotting and data visualization."
    license = "GPL-3.0-only"
    topics = ("chart", "data-visualization", "graph", "plot", "qt")
    homepage = "https://www.qcustomplot.com"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_opengl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_opengl": False,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def build_requirements(self):
        self.tool_requires("qt/<host_version>")
        self.tool_requires("cmake/[>=3.27 <4]") # to be able to use CMAKE_AUTOMOC_EXECUTABLE

    def requirements(self):
        if Version(self.version) >= "2.0.0":
            # INFO: Public header qcustomplot.h includes QObject
            self.requires("qt/[>=6.5 <7]", transitive_headers=True, options={"widgets": True, "gui": True})
        else:
            # INFO: Public header qcustomplot.h includes QObject
            self.requires("qt/[~5.15]", transitive_headers=True, options={"widgets": True, "gui": True})
        if self.options.with_opengl and self.settings.os == "Windows":
            self.requires("opengl/system")

    def validate(self):
        min_cppstd = "11" if Version(self.dependencies["qt"].ref.version) < "6" else "17"
        check_min_cppstd(self, min_cppstd)
        if self.info.options.with_opengl and self.dependencies["qt"].options.opengl == "no":
            raise ConanInvalidConfiguration(f"{self.ref} with opengl requires Qt with opengl enabled: -o 'qt/*:opengl=desktop/dynamic'")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["QCUSTOMPLOT_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.cache_variables["QCUSTOMPLOT_VERSION"] = str(self.version)
        tc.cache_variables["QCUSTOMPLOT_VERSION_MAJOR"] = str(Version(self.version).major)
        tc.cache_variables["QT_VERSION"] = str(self.dependencies["qt"].ref.version)
        tc.cache_variables["QCUSTOMPLOT_USE_OPENGL"] = self.options.with_opengl
        qt_tools_rootdir = self.conf.get("user.qt:tools_directory", self.dependencies["qt"].cpp_info.bindirs[0])
        tc.cache_variables["CMAKE_AUTOMOC_EXECUTABLE"] = os.path.join(qt_tools_rootdir, "moc.exe" if self.settings_build.os == "Windows" else "moc")
        tc.cache_variables["CMAKE_AUTORCC_EXECUTABLE"] = os.path.join(qt_tools_rootdir, "rcc.exe" if self.settings_build.os == "Windows" else "rcc")
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if Version(self.version) >= "2.0.0":
            # allow static qcustomplot with shared qt, and vice versa
            replace_in_file(self, os.path.join(self.source_folder, "qcustomplot.h"),
                                  "#if defined(QT_STATIC_BUILD)",
                                  "#if 0" if self.options.shared else "#if 1")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "GPL.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        postfix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"qcustomplot{postfix}"]
        self.cpp_info.requires = ["qt::qtCore", "qt::qtGui", "qt::qtWidgets", "qt::qtPrintSupport"]
        if self.options.shared:
            self.cpp_info.defines.append("QCUSTOMPLOT_USE_LIBRARY")
        if self.options.with_opengl:
            self.cpp_info.defines.append("QCUSTOMPLOT_USE_OPENGL")
            if self.settings.os == "Windows":
                self.cpp_info.requires.append("opengl::opengl")
