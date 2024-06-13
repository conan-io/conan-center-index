from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, save
from conan.tools.scm import Version

import os
import textwrap

required_conan_version = ">=1.54.0"


class TesseractConan(ConanFile):
    name = "tesseract"
    description = "Tesseract Open Source OCR Engine"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tesseract-ocr/tesseract"
    topics = ("ocr", "image", "multimedia", "graphics")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_auto_optimize": [True, False],
        "with_march_native": [True, False],
        "with_training": [True, False],
        "with_libcurl": [True, False],
        "with_libarchive": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_auto_optimize": False,
        "with_march_native": False,
        "with_training": False,
        "with_libcurl": True,
        "with_libarchive": True,
    }

    @property
    def _min_cppstd(self):
        return "11" if Version(self.version) < "5.0.0" else "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "11": {
                "Visual Studio": "14",
                "msvc": "190",
                "gcc": "5",
                "clang": "5",
                "apple-clang": "6",
            },
            "17": {
                "Visual Studio": "16",
                "msvc": "192",
                "gcc": "7",
                "clang": "7",
                "apple-clang": "11",
            },
        }.get(self._min_cppstd, {})

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "5.0.0":
            del self.options.with_libcurl
            del self.options.with_libarchive

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) >= "5.2.0":
            self.requires("leptonica/1.83.1")
        else:
            self.requires("leptonica/1.82.0")
        if self.settings.os == "Windows" and Version(self.version) >= "5.0.0":
            self.requires("libtiff/4.6.0")
        # libarchive is required for 4.x so default value is true
        if self.options.get_safe("with_libarchive", default=True):
            self.requires("libarchive/3.7.2")
        # libcurl is not required for 4.x
        if self.options.get_safe("with_libcurl", default=False):
            self.requires("libcurl/[>=7.78.0 <9]")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.options.with_training:
            # do not enforce failure and allow user to build with system cairo, pango, fontconfig
            self.output.warning("*** Build with training is not yet supported, continue on your own")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TRAINING_TOOLS"] = self.options.with_training
        tc.variables["INSTALL_CONFIGS"] = self.options.with_training

        # pre-5.0.0 uses custom STATIC variable instead of BUILD_SHARED_LIBS
        if Version(self.version) < "5.0.0":
            tc.variables["STATIC"] = not self.options.shared

        # Use CMake-based package build and dependency detection, not the pkg-config, cppan or SW
        tc.variables["CPPAN_BUILD"] = False
        tc.variables["SW_BUILD"] = False

        # disable autodetect of vector extensions and march=native
        tc.variables["ENABLE_OPTIMIZATIONS"] = self.options.with_auto_optimize

        if Version(self.version) < "5.0.0":
            tc.variables["AUTO_OPTIMIZE"] = self.options.with_auto_optimize

        # Set Leptonica_DIR to ensure that find_package will be called in original CMake file
        tc.variables["Leptonica_DIR"] = self.dependencies["leptonica"].package_folder.replace("\\", "/")

        if Version(self.version) >= "5.0.0":
            tc.variables["DISABLE_CURL"] = not self.options.with_libcurl
            tc.variables["DISABLE_ARCHIVE"] = not self.options.with_libarchive
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"libtesseract": "Tesseract::libtesseract"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        # Official CMake imported target is:
        # - libtesseract if < 5.0.0
        # - Tesseract::libtesseract if >= 5.0.0
        # We provide both targets
        self.cpp_info.set_property("cmake_file_name", "Tesseract")
        self.cpp_info.set_property("cmake_target_name", "Tesseract::libtesseract")
        self.cpp_info.set_property("cmake_target_aliases", ["libtesseract"])
        self.cpp_info.set_property("pkg_config_name", "tesseract")

        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["libtesseract"].libs = [self._libname]
        self.cpp_info.components["libtesseract"].requires = ["leptonica::leptonica"]
        if self.settings.os == "Windows" and Version(self.version) >= "5.0.0":
            self.cpp_info.components["libtesseract"].requires.append("libtiff::libtiff")
        if self.options.get_safe("with_libcurl", default=False):
            self.cpp_info.components["libtesseract"].requires.append("libcurl::libcurl")
        if self.options.get_safe("with_libarchive", default=True):
            self.cpp_info.components["libtesseract"].requires.append("libarchive::libarchive")
        if self.options.shared:
            self.cpp_info.components["libtesseract"].defines = ["TESS_IMPORTS"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libtesseract"].system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["libtesseract"].system_libs = ["ws2_32"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "Tesseract"
        self.cpp_info.names["cmake_find_package_multi"] = "Tesseract"
        self.cpp_info.components["libtesseract"].names["cmake_find_package"] = "libtesseract"
        self.cpp_info.components["libtesseract"].names["cmake_find_package_multi"] = "libtesseract"
        self.cpp_info.components["libtesseract"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["libtesseract"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["libtesseract"].set_property("pkg_config_name", "tesseract")
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

    @property
    def _libname(self):
        suffix = ""
        if self.settings.os == "Windows":
            v = Version(self.version)
            suffix += f"{v.major}{v.minor}"
            if self.settings.build_type == "Debug":
                suffix += "d"
        return f"tesseract{suffix}"
