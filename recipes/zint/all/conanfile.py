from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class ZintConan(ConanFile):
    name = "zint"
    description = "Zint Barcode Generator"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.zint.org.uk"
    license = "BSD", "GPL-3.0"
    topics = ("barcode", "qt")
    package_type = "library"
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

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_qt:
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_libpng:
            self.requires("libpng/[>=1.6 <2]")
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_qt:
            self.requires("qt/5.15.11")

    def validate(self):
        if self.options.with_qt and not self.dependencies["qt"].options.gui:
            raise ConanInvalidConfiguration(f"{self.ref} needs qt:gui=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_PROJECT_test_package_INCLUDE"] = "conan_deps.cmake"
        tc.cache_variables["ZINT_USE_QT"] = self.options.with_qt
        if self.options.with_qt:
            tc.cache_variables["QT_VERSION_MAJOR"] = Version(self.dependencies["qt"].ref.version).major
        if Version(self.version) >= "2.13.0":
            tc.variables["ZINT_SHARED"] = self.options.shared
            tc.variables["ZINT_STATIC"] = not self.options.shared
        tc.variables["ZINT_USE_PNG"] = self.options.with_libpng
        tc.variables["DATA_INSTALL_DIR"] = "lib"
        tc.variables["INCLUDE_INSTALL_DIR"] = "include"
        tc.variables["SHARE_INSTALL_PREFIX"] = "share"
        if self.options.shared and self.settings.os == "Windows":
            tc.preprocessor_definitions["ZINT_BUILD_DLL"] = "1"
            tc.preprocessor_definitions["QZINT_BUILD_DLL"] = "1"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_source(self):
        apply_conandata_patches(self)
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        # Disable subdirectories
        save(self, os.path.join(self.source_folder, "frontend", "CMakeLists.txt"), "")
        save(self, os.path.join(self.source_folder, "frontend_qt", "CMakeLists.txt"), "")
        save(self, os.path.join(self.source_folder, "getopt", "CMakeLists.txt"), "")
        # Don't override CMAKE_OSX_SYSROOT, it can easily break consumers.
        replace_in_file(self, cmakelists, 'set(CMAKE_OSX_SYSROOT "/")', "")
        # Get Qt in conan_deps.cmake instead
        replace_in_file(self, cmakelists, "find_package(Qt", "# find_package(Qt")
        replace_in_file(self, cmakelists, "if(Qt", "if(1) # if(Qt")
        # Don't override CMAKE_MODULE_PATH
        replace_in_file(self, cmakelists, 'set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/modules")', "", strict=False)
        replace_in_file(self, cmakelists, 'include(SetPaths.cmake)', "")
        # Do not set DLL_EXPORT, use a more specific macro from the patch instead
        replace_in_file(self, os.path.join(self.source_folder, "backend", "CMakeLists.txt"),
                        "target_compile_definitions(zint PRIVATE DLL_EXPORT)", "")
        replace_in_file(self, os.path.join(self.source_folder, "backend/zint.h"),
                        "#  if defined(DLL_EXPORT) || defined(PIC) || defined(_USRDLL)",
                        "#  if defined(ZINT_BUILD_DLL)")

    def build(self):
        self._patch_source()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        if Version(self.version) >= "2.13.0":
            copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        else:
            copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
            copy(self, "*/LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Zint")

        lib_suffix = ""
        if not self.options.shared:
            if self.settings.os == "Windows" or self.version == "2.10.0":
                lib_suffix = "-static"

        self.cpp_info.components["libzint"].set_property("cmake_target_name", "Zint::Zint")
        self.cpp_info.components["libzint"].libs = ["zint" + lib_suffix]
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
