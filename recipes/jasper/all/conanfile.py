from conans import CMake
from conan import ConanFile
from conan.tools.files import get, save, rmdir, rm, replace_in_file, apply_conandata_patches, export_conandata_patches
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.53.0"


class JasperConan(ConanFile):
    name = "jasper"
    license = "JasPer-2.0"
    homepage = "https://jasper-software.github.io/jasper"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("tool-kit", "coding")
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

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def requirements(self):
        if self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.2")
        elif self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")

    def validate(self):
        if self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) == "16":
            raise ConanInvalidConfiguration(f"{self.name} Current can not build in CCI due to windows SDK version. See https://github.com/conan-io/conan-center-index/pull/13285 for the solution hopefully")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["JAS_ENABLE_DOC"] = False
        self._cmake.definitions["JAS_ENABLE_PROGRAMS"] = False
        self._cmake.definitions["JAS_ENABLE_SHARED"] = self.options.shared
        self._cmake.definitions["JAS_LIBJPEG_REQUIRED"] = "REQUIRED"
        self._cmake.definitions["JAS_ENABLE_OPENGL"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Clean rpath in installed shared lib
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        cmds_to_remove = [
            "set(CMAKE_INSTALL_RPATH \"${CMAKE_INSTALL_PREFIX}/lib\")",
            "set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)",
            "set(CMAKE_INSTALL_RPATH\n		  \"${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}\")",
        ]
        for cmd_to_remove in cmds_to_remove:
            replace_in_file(self, cmakelists, cmd_to_remove, "")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.settings.os == "Windows":
            for dll_prefix in ["concrt", "msvcp", "vcruntime"]:
                rm(self, f"{dll_prefix}*.dll", os.path.join(self.package_folder, "bin"))
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    def _create_cmake_module_variables(self, module_file):
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
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-variables.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
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
