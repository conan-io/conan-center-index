from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.33.0"


class QcustomplotConan(ConanFile):
    name = "qcustomplot"
    description = "QCustomPlot is a Qt C++ widget for plotting and data visualization."
    license = "GPL-3.0-only"
    topics = ("qcustomplot", "qt", "chart", "plot", "data-visualization")
    homepage = "https://www.qcustomplot.com"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        # FIXME: we shouldn't have to force shared in qt, but config file
        #        generated by conan in qt static is likely broken, or maybe env vars.
        self.options["qt"].shared = True

    def requirements(self):
        self.requires("qt/6.2.3")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            min_cppstd = "11" if tools.Version(self.deps_cpp_info["qt"].version) < "6.0.0" else "17"
            tools.check_min_cppstd(self, min_cppstd)
        if not (self.options["qt"].gui and self.options["qt"].widgets):
            raise ConanInvalidConfiguration("qcustomplot requires qt gui and widgets")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # allow static qcustomplot with shared qt, and vice versa
        tools.replace_in_file(os.path.join(self._source_subfolder, "qcustomplot.h"),
                              "#if defined(QT_STATIC_BUILD)",
                              "#if 0" if self.options.shared else "#if 1")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["QT_VERSION"] = self.deps_cpp_info["qt"].version
        # TODO: add an option to enable QCUSTOMPLOT_USE_OPENGL
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("GPL.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        postfix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = ["qcustomplot" + postfix]
        if self.options.shared:
            self.cpp_info.defines.append("QCUSTOMPLOT_USE_LIBRARY")
        self.cpp_info.requires = ["qt::qtCore", "qt::qtGui", "qt::qtWidgets", "qt::qtPrintSupport"]
