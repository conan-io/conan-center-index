from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class OcctConan(ConanFile):
    name = "occt"
    description = """a software development platform providing services for 3D
        surface and solid modeling, CAD data exchange, and visualization."""
    homepage = "https://github.com/Open-Cascade-SAS/OCCT"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-2.1-or-later"
    topics = ("3D", "modeling")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    requires = [("tcl/8.6.10"),
                ("tk/8.6.10"),
                ("freetype/2.10.4")]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name.upper() + "-" + \
            self.version.replace(".", "_")
        tools.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "project (OCCT)",
            '''project (OCCT)
                include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
                conan_basic_setup()''')
        tcl_libs = self.deps_cpp_info["tcl"].libs
        tcl_lib = next(filter(lambda lib: "tcl8" in lib, tcl_libs))
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "adm/cmake/tcl.cmake"),
            "${CSF_TclLibs}",
            tcl_lib)

        tk_libs = self.deps_cpp_info["tk"].libs
        tk_lib = next(filter(lambda lib: "tk8" in lib, tk_libs))
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "adm/cmake/tk.cmake"),
            "${CSF_TclTkLibs}",
            tk_lib)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["3RDPARTY_TCL_LIBRARY_DIR"] = \
            os.path.join(self.deps_cpp_info["tcl"].rootpath, "lib")
        self._cmake.definitions["3RDPARTY_TCL_INCLUDE_DIR"] = \
            self.deps_cpp_info["tcl"].include_paths[0]
        self._cmake.definitions["3RDPARTY_TK_LIBRARY_DIR"] = \
            os.path.join(self.deps_cpp_info["tk"].rootpath, "lib")
        self._cmake.definitions["3RDPARTY_TK_INCLUDE_DIR"] = \
            self.deps_cpp_info["tk"].include_paths[0]
        if not self.options.shared:
            self._cmake.definitions["BUILD_LIBRARY_TYPE"] = "Static"

        self._cmake.definitions["INSTALL_DIR_BIN"] = "bin"
        self._cmake.definitions["INSTALL_DIR_INCLUDE"] = "include"
        self._cmake.definitions["INSTALL_DIR_LIB"] = "lib"
        self._cmake.definitions["INSTALL_DIR_RESOURCE"] = "res"

        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        if self.options.shared:
            if not self.options["tcl"].shared or \
                    not self.options["tk"].shared or \
                    not self.options["freetype"].shared:
                raise ConanInvalidConfiguration(
                    "tcl, tk and freetype must be shared when occt is shared.")
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(
            "LICENSE_LGPL_21.txt",
            src=self._source_subfolder,
            dst="licenses")
        self.copy(
            "OCCT_LGPL_EXCEPTION.txt",
            src=self._source_subfolder,
            dst="licenses")
        with tools.chdir(self.package_folder):
            for item in os.listdir():
                if os.path.isfile(item):
                    os.remove(item)
                elif item not in ["lib", "bin", "include", "res", "licenses"]:
                    shutil.rmtree(item)

    def package_info(self):
        self.cpp_info.libs = os.listdir("lib")
