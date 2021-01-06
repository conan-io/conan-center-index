from conans import ConanFile, CMake, tools
import os


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
                ("freetype/2.10.2")]
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
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "adm/cmake/tk.cmake"),
            "${CSF_TclTkLibs}",
            self.deps_cpp_info["tk"].libs[0])
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "adm/cmake/tcl.cmake"),
            "${CSF_TclLibs}",
            self.deps_cpp_info["tcl"].libs[0])

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["3RDPARTY_TCL_LIBRARY_DIR"] = \
            self.deps_cpp_info["tcl"].lib_paths[0]
        self._cmake.definitions["3RDPARTY_TCL_INCLUDE_DIR"] = \
            self.deps_cpp_info["tcl"].include_paths[0]
        self._cmake.definitions["3RDPARTY_TK_LIBRARY_DIR"] = \
            self.deps_cpp_info["tk"].lib_paths[0]
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
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        with tools.chdir(self.package_folder):
            tools.mkdir("licenses")
            tools.rename(
                "LICENSE_LGPL_21.txt",
                os.path.join("licenses", "LICENSE_LGPL_21.txt"))
            tools.rename(
                "OCCT_LGPL_EXCEPTION.txt",
                os.path.join("licenses", "OCCT_LGPL_EXCEPTION.txt"))
            tools.rmdir("cmake")
            for file in os.listdir():
                if ".bat" in file:
                    os.remove(file)

    def package_info(self):
        libs: List[str] = []
        libdirs = []
        bindirs = []
        for root, dirs, _ in os.walk(self.package_folder):
            if "lib" in dirs:
                libdir = os.path.join(root, "lib")
                libdirs.append(libdir)
                libs.extend(tools.collect_libs(self, libdir))
            if "bin" in dirs:
                bindir = os.path.join(root, "bin")
                bindirs.append(bindir)
        self.cpp_info.libs = libs
        self.cpp_info.libdirs = libdirs
        self.cpp_info.bindirs = bindirs
