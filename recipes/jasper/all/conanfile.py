from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.53.0"


class JasperConan(ConanFile):
    name = "jasper"
    license = "JasPer-2.0"
    homepage = "https://jasper-software.github.io/jasper"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("toolkit", "coding", "jpeg", "images")
    description = "JasPer Image Processing/Coding Tool Kit"
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
            self.requires("libjpeg/9e")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.5")
        elif self.options.with_libjpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) >= "4.0.0":
            tc.variables["JAS_ENABLE_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["JAS_ENABLE_DOC"] = False
        tc.variables["JAS_ENABLE_LATEX"] = False
        tc.variables["JAS_ENABLE_PROGRAMS"] = False
        tc.variables["JAS_ENABLE_SHARED"] = self.options.shared
        tc.variables["JAS_LIBJPEG_REQUIRED"] = "REQUIRED"
        tc.variables["JAS_ENABLE_LIBJPEG"] = bool(self.options.with_libjpeg)
        if Version(self.version) >= "3.0.0":
            tc.variables["JAS_ENABLE_LIBHEIF"] = False
        tc.variables["JAS_ENABLE_OPENGL"] = False

        if cross_building(self):
            tc.cache_variables["JAS_CROSSCOMPILING"] = True
            tc.cache_variables["JAS_STDC_VERSION"] = "199901L"

        # TODO: Remove after fixing https://github.com/conan-io/conan-center-index/issues/13159
        # C3I workaround to force CMake to choose the highest version of
        # the windows SDK available in the system
        if is_msvc(self) and not self.conf.get("tools.cmake.cmaketoolchain:system_version"):
            tc.variables["CMAKE_SYSTEM_VERSION"] = "10.0"

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
        self._create_cmake_module_variables(os.path.join(self.package_folder, self._module_file_rel_path))

    # FIXME: Missing CMake alias variables. See https://github.com/conan-io/conan/issues/7691
    def _create_cmake_module_variables(self, module_file):
        content = textwrap.dedent(f"""\
            set(JASPER_FOUND TRUE)
            if(DEFINED Jasper_INCLUDE_DIR)
                set(JASPER_INCLUDE_DIR ${{Jasper_INCLUDE_DIR}})
            endif()
            if(DEFINED Jasper_LIBRARIES)
                set(JASPER_LIBRARIES ${{Jasper_LIBRARIES}})
            endif()
            set(JASPER_VERSION_STRING "{self.version}")
        """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Jasper")
        self.cpp_info.set_property("cmake_target_name", "Jasper::Jasper")
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

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "Jasper"
        self.cpp_info.names["cmake_find_package_multi"] = "Jasper"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
