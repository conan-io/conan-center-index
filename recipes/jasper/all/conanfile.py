from conans import ConanFile, CMake, tools
import glob
import os
import textwrap

required_conan_version = ">=1.33.0"


class JasperConan(ConanFile):
    name = "jasper"
    license = "JasPer License Version 2.0"
    homepage = "https://jasper-software.github.io/jasper"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "jasper", "tool-kit", "coding")
    description = "JasPer Image Processing/Coding Tool Kit"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo"],
        "jpegturbo": [True, False, "deprecated"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libjpeg": "libjpeg",
        "jpegturbo": "deprecated",
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

        # Handle deprecated libjpeg option
        if self.options.jpegturbo != "deprecated":
            self.output.warn("jpegturbo option is deprecated, use with_libjpeg option instead.")
            self.options.with_libjpeg = "libjpeg-turbo" if self.options.jpegturbo else "libjpeg"

    def requirements(self):
        if self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.0")
        elif self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9d")

    def package_id(self):
        del self.info.options.jpegturbo

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
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

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.settings.os == "Windows":
            for dll_file in glob.glob(os.path.join(self.package_folder, "bin", "*.dll")):
                if os.path.basename(dll_file).startswith(("concrt", "msvcp", "vcruntime")):
                    os.unlink(dll_file)
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    @staticmethod
    def _create_cmake_module_variables(module_file):
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
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-variables.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Jasper"
        self.cpp_info.names["cmake_find_package_multi"] = "Jasper"
        self.cpp_info.names["pkg_config"] = "jasper"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.libs = ["jasper"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
