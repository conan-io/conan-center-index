from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import export_conandata_patches, apply_conandata_patches, copy, get, rmdir
from conan.tools.scm import Version
from conan.tools.env import VirtualRunEnv
from conan.tools.microsoft import is_msvc
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.0.9"


class QXlsxConan(ConanFile):
    name = "qxlsx"
    description = "Excel file (*.xlsx) reader/writer library using Qt 5 or 6."
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
    implements = ["auto_shared_fpic"]

    @property
    def _qt_version(self):
        return str(Version(self.dependencies["qt"].ref.version).major)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # INFO: QXlsx/xlsxdocument.h includes QtGlobal
        # INFO: transitive libs: undefined reference to symbol '_ZN10QArrayData10deallocateEPS_mm@@Qt_5'
        self.requires("qt/[>=6.7 <7]", transitive_headers=True, transitive_libs=True)

    def validate(self):
        check_min_cppstd(self, 11)
        if not self.dependencies["qt"].options.gui:
            raise ConanInvalidConfiguration(f"{self.ref} requires Qt with gui component. Use '-o qt/*:gui=True'")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")
        # INFO: QXlsx use Qt automoc: https://github.com/QtExcel/QXlsx/blob/v1.4.9/QXlsx/CMakeLists.txt#L12
        self.tool_requires("qt/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # INFO: In order to find Qt moc application
        env = VirtualRunEnv(self)
        env.generate(scope="build")

        tc = CMakeToolchain(self)
        tc.cache_variables["QT_VERSION_MAJOR"] = self._qt_version
        # INFO: QXlsx use cached CMAKE_CXX_STANDARD value:
        # https://github.com/QtExcel/QXlsx/blob/v1.4.9/QXlsx/CMakeLists.txt#L23
        tc.cache_variables["CMAKE_CXX_STANDARD"] = self.settings.get_safe("compiler.cppstd").replace("gnu", "")
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "QXlsx"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        cmake_name = f"QXlsxQt{self._qt_version}"
        self.cpp_info.set_property("cmake_file_name", cmake_name)
        self.cpp_info.set_property("cmake_target_name", "QXlsx::QXlsx")
        self.cpp_info.set_property("cmake_target_aliases", ["QXlsx"])
        self.cpp_info.libs = [cmake_name]
        includedir = f"QXlsxQt{self._qt_version}" if Version(self.version) >= "1.4.6" else "QXlsx"
        self.cpp_info.includedirs = ["include", os.path.join("include", includedir)]
        self.cpp_info.requires = ["qt::qtCore", "qt::qtGui"]
        if is_msvc(self) and self.options.shared:
            self.cpp_info.defines = ["QXlsx_SHAREDLIB"]
