from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.43.0"


class ZintConan(ConanFile):
    name = "zint"
    description = "Zint Barcode Generator"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/p/zint/code"
    license = "GPL-3.0"
    topics = ("barcode", "qt")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libpng": [True, False],
        "with_qt": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libpng": True,
        "with_qt": False,
    }

    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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
        if not self.options.with_qt:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_libpng:
            self.requires("libpng/1.6.37")
            self.requires("zlib/1.2.12")
        if self.options.with_qt:
            self.requires("qt/5.15.3")

    def validate(self):
        if self.options.with_qt and not self.options["qt"].gui:
            raise ConanInvalidConfiguration(f"{self.name} needs qt:gui=True")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _patch_source(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # Don't override CMAKE_OSX_SYSROOT, it can easily break consumers.
        tools.files.replace_in_file(self, 
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "set(CMAKE_OSX_SYSROOT \"/\")",
            "",
        )

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["DATA_INSTALL_DIR"] = os.path.join(self.package_folder, "lib")
        cmake.definitions["ZINT_USE_QT"] = self.options.with_qt
        if self.options.with_qt:
            cmake.definitions["QT_VERSION_MAJOR"] = tools.scm.Version(self, self.deps_cpp_info["qt"].version).major
        cmake.definitions["ZINT_USE_PNG"] = self.options.with_libpng
        cmake.configure()
        return cmake

    def build(self):
        self._patch_source()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Zint")

        self.cpp_info.components["libzint"].set_property("cmake_target_name", "Zint::Zint")
        self.cpp_info.components["libzint"].libs = ["zint" if self.options.shared else "zint-static"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["libzint"].defines = ["ZINT_DLL"]
        if self.options.with_libpng:
            self.cpp_info.components["libzint"].requires.extend(["libpng::libpng", "zlib::zlib"])

        if self.options.with_qt:
            self.cpp_info.components["libqzint"].set_property("cmake_target_name", "Zint::QZint")
            self.cpp_info.components["libqzint"].libs = ["QZint"]
            self.cpp_info.components["libqzint"].requires.extend([
                "libzint",
                "qt::qtGui",
            ])
            if self.settings.os == "Windows" and self.options.shared:
                self.cpp_info.components["libqzint"].defines = ["QZINT_DLL"]

        # Trick to only define Zint::QZint and Zint::Zint in CMakeDeps generator
        self.cpp_info.set_property("cmake_target_name", "Zint::QZint" if self.options.with_qt else "Zint::Zint")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Zint"
        self.cpp_info.names["cmake_find_package_multi"] = "Zint"
        self.cpp_info.components["libzint"].names["cmake_find_package"] = "Zint"
        self.cpp_info.components["libzint"].names["cmake_find_package_multi"] = "Zint"
        if self.options.with_qt:
            self.cpp_info.components["libqzint"].names["cmake_find_package"] = "QZint"
            self.cpp_info.components["libqzint"].names["cmake_find_package_multi"] = "QZint"
