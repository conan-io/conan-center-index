import os
from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain
from conan.tools.build import check_min_cppstd

required_conan_version = ">=2.0.9"

class NodeEditorConan(ConanFile):
    name = "nodeeditor"
    license = "BSD-3-Clause"
    description = "Dataflow programming framework and UI for Qt"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/paceholder/nodeeditor"
    topics = ("qt", "ui", "dataflow")
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    package_type = "library"
    implements = ["auto_shared_fpic"]

    @property
    def _qt_version_major(self):
        return str(self.dependencies["qt"].ref.version.major)

    def export_sources(self):
        copy(self, "conan_cmake_project_include.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        # INFO: Qt headers are exposed largely in public headers. e.g QtCore/QObject consumed by NodaData.hpp
        self.requires("qt/[>=6.7 <7]", transitive_headers=True)

    def build_requirements(self):
        # INFO: Uses Qt rcc tool to generate resources.cpp file via resources.qrc
        self.tool_requires("qt/<host_version>")
        # INFO: To be able to use CMAKE_AUTOMOC_EXECUTABLE
        self.tool_requires("cmake/[>=3.27 <4]")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_DOCS"] = False
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        # INFO: replcate requires could be used to replace the Qt version by 5.x
        tc.cache_variables["USE_QT6"] = self._qt_version_major == "6"
        # INFO: In order to execute the moc tool and avoid failing to find its dependencies
        qt_tools_rootdir = self.conf.get("user.qt:tools_directory", None)
        tc.cache_variables["CMAKE_PROJECT_QtNodesLibrary_INCLUDE"] = os.path.join(self.source_folder, "conan_cmake_project_include.cmake")
        tc.cache_variables["CMAKE_AUTOMOC_EXECUTABLE"] = os.path.join(qt_tools_rootdir, "moc.exe" if self.settings_build.os == "Windows" else "moc")
        tc.cache_variables["CMAKE_AUTORCC_EXECUTABLE"] = os.path.join(qt_tools_rootdir, "rcc.exe" if self.settings_build.os == "Windows" else "rcc")
        tc.generate()

    def validate(self):
        required_cppstd = "17" if self._qt_version_major == "6" else "14"
        check_min_cppstd(self, required_cppstd)

    def build(self):
        cm = CMake(self)
        cm.configure()
        cm.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cm = CMake(self)
        cm.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["QtNodes"]
        self.cpp_info.requires.extend(["qt::qtCore", "qt::qtGui",
                                       "qt::qtWidgets", "qt::qtOpenGL"])
        self.cpp_info.set_property("cmake_file_name", "QtNodes")
        self.cpp_info.set_property("cmake_target_name", "QtNodes::QtNodes")
        if self.options.shared:
            self.cpp_info.defines = ["NODE_EDITOR_SHARED"]
        else:
            self.cpp_info.defines = ["NODE_EDITOR_STATIC"]
