from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, save
from conan.tools.scm import Version
import os

required_conan_version = ">=2.2"


class JasperConan(ConanFile):
    name = "jasper"
    description = "JasPer Image Processing/Coding Tool Kit"
    license = "JasPer-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://jasper-software.github.io/jasper"
    topics = ("toolkit", "coding", "jpeg", "images")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libjpeg": [False, "libjpeg", "libjpeg-turbo", "mozjpeg"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libjpeg": "libjpeg",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/[>=9e]")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/[>=3.0.2 <4]")
        elif self.options.with_libjpeg == "mozjpeg":
            self.requires("mozjpeg/[>=4.1.5 <5]")

    def build_requirements(self):
        if Version(self.version) >= "4.1.1":
            self.tool_requires("cmake/[>=3.20]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = CMakeToolchain(self)
        tc.variables["JAS_ENABLE_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["JAS_ENABLE_DOC"] = False
        tc.variables["JAS_ENABLE_LATEX"] = False
        tc.variables["JAS_ENABLE_PROGRAMS"] = False
        tc.variables["JAS_ENABLE_SHARED"] = self.options.shared
        tc.variables["JAS_LIBJPEG_REQUIRED"] = "REQUIRED"
        tc.variables["JAS_ENABLE_LIBJPEG"] = bool(self.options.with_libjpeg)
        tc.variables["JAS_HAVE_JPEGLIB_H"] = True
        tc.variables["JAS_ENABLE_LIBHEIF"] = False
        tc.variables["JAS_ENABLE_OPENGL"] = False
        if cross_building(self):
            tc.cache_variables["JAS_CROSSCOMPILING"] = True
            tc.cache_variables["JAS_STDC_VERSION"] = "199901L"
        if Version(self.version) >= "4.2.0":
            tc.variables["JAS_PACKAGING"] = True
        tc.generate()

        cmakedeps = CMakeDeps(self)
        cmakedeps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYRIGHT*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.settings.os == "Windows":
            for dll_prefix in ["concrt", "msvcp", "vcruntime"]:
                rm(self, f"{dll_prefix}*.dll", os.path.join(self.package_folder, "bin"))
        save(self, os.path.join(self.package_folder, self._module_file_rel_path), "set(JASPER_FOUND TRUE)")

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Jasper")
        self.cpp_info.set_property("cmake_target_name", "Jasper::Jasper")
        self.cpp_info.set_property("cmake_additional_variables_prefixes", ["JASPER"])
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.set_property("pkg_config_name", "jasper")
        self.cpp_info.libs = ["jasper"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        self.cpp_info.requires = []
        if self.options.with_libjpeg == "libjpeg":
            self.cpp_info.requires.append("libjpeg::libjpeg")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.cpp_info.requires.append("libjpeg-turbo::jpeg")
        elif self.options.with_libjpeg == "mozjpeg":
            self.cpp_info.requires.append("mozjpeg::libjpeg")
