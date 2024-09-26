from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"


class QXlsxConan(ConanFile):
    name = "qxlsx"
    description = "Excel file(*.xlsx) reader/writer library using Qt 5 or 6."
    license = "MIT"
    topics = ("excel", "xlsx")
    homepage = "https://github.com/QtExcel/QXlsx"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _qt_version(self):
        return str(Version(self.dependencies["qt"].ref.version).major)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # INFO: QXlsx/xlsxdocument.h includes QtGlobal
        # INFO: transitive libs: undefined reference to symbol '_ZN10QArrayData10deallocateEPS_mm@@Qt_5'
        self.requires("qt/[~5.15]", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if not self.dependencies["qt"].options.gui:
            raise ConanInvalidConfiguration(f"{self.ref} requires Qt with gui component. Use '-o qt/*:gui=True'")
        if Version(self.version) == "1.4.4" and is_msvc(self) and self.options.shared:
            # FIXME: xlsxworksheet.cpp.obj : error LNK2019: unresolved external symbol " __cdecl QVector<class QXmlStreamAttribute>::begin(
            raise ConanInvalidConfiguration(f"{self.ref} Conan recipe does not support shared library with MSVC. Use version 1.4.5 or later.")

    def build_requirements(self):
        if Version(self.version) >= "1.4.4":
            self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = VirtualBuildEnv(self)
        tc.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["QT_VERSION_MAJOR"] = self._qt_version
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "QXlsx"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        cmake_name = f"QXlsxQt{self._qt_version}" if Version(self.version) >= "1.4.5" else "QXlsx"
        self.cpp_info.set_property("cmake_file_name", cmake_name)
        self.cpp_info.set_property("cmake_target_name", "QXlsx::QXlsx")
        self.cpp_info.libs = [cmake_name]
        self.cpp_info.includedirs = ["include", os.path.join("include", "QXlsx")]
        self.cpp_info.requires = ["qt::qtCore", "qt::qtGui"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = cmake_name
        self.cpp_info.filenames["cmake_find_package_multi"] = cmake_name
        self.cpp_info.names["cmake_find_package"] = "QXlsx"
        self.cpp_info.names["cmake_find_package"] = "QXlsx"
