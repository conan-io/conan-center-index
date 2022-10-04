from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir, rm, save, export_conandata_patches, apply_conandata_patches
from conan.tools.build import cross_building
import os
import textwrap

required_conan_version = ">=1.52.0"


class JasperConan(ConanFile):
    name = "jasper"
    license = "JasPer-2.0"
    homepage = "https://jasper-software.github.io/jasper"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("toolkit", "coding", "jpeg", "images")
    description = "JasPer Image Processing/Coding Tool Kit"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo"],
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
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.4")
        elif self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["JAS_ENABLE_DOC"] = False
        tc.variables["JAS_ENABLE_LATEX"] = False
        tc.variables["JAS_ENABLE_PROGRAMS"] = False
        tc.variables["JAS_ENABLE_SHARED"] = self.options.shared
        tc.variables["JAS_LIBJPEG_REQUIRED"] = "REQUIRED"
        tc.variables["JAS_ENABLE_OPENGL"] = False
        tc.variables["JAS_ENABLE_LIBJPEG"] = True
        if cross_building(self):
            tc.cache_variables["JAS_CROSSCOMPILING"] = True
            tc.cache_variables["JAS_STDC_VERSION"] = "199901L"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

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
                rm(self, "{}*.dll".format(dll_prefix), os.path.join(self.package_folder, "bin"))
        self._create_cmake_module_variables(self,
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    @staticmethod
    def _create_cmake_module_variables(conanfile, module_file):
        content = textwrap.dedent("""\
            if(DEFINED Jasper_FOUND)
                set(JASPER_FOUND ${Jasper_FOUND})
            endif()
            if(DEFINED Jasper_INCLUDE_DIR)
                set(JASPER_INCLUDE_DIR ${Jasper_INCLUDE_DIR})
            endif()
            if(DEFINED Jasper_LIBRARIES)
                set(JASPER_LIBRARIES ${Jasper_LIBRARIES})
            endif()
            if(DEFINED Jasper_VERSION)
                set(JASPER_VERSION_STRING ${Jasper_VERSION})
            endif()
        """)
        save(conanfile, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-variables.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Jasper")
        self.cpp_info.set_property("cmake_target_name", "Jasper::Jasper")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.set_property("pkg_config_name", "jasper")

        self.cpp_info.names["cmake_find_package"] = "Jasper"
        self.cpp_info.names["cmake_find_package_multi"] = "Jasper"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]

        self.cpp_info.libs = ["jasper"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
