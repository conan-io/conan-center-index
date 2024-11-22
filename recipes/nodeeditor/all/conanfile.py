import os
from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain
from conan.tools.env import VirtualRunEnv

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
    impplements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        # INFO: Qt headers are exposed largely in public headers. e.g QtCore/QObject consumed by NodaData.hpp
        # INFO: NodeEditor exposes Qt methods directly.
        #       e.g Windows-shared error LNK2001: unresolved external symbol __imp_qt_version_tag_6_7
        self.requires("qt/[>=6.7 <7]", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        # INFO: Uses Qt rcc tool to generate resources.cpp file via resources.qrc
        self.tool_requires("qt/<host_version>")

    def generate(self):
        # INFO: Qt executable could not find pcre2-16.dll without environment
        # CMake Error: AUTOMOC for target QtNodes: Test run of "moc" executable
        env = VirtualRunEnv(self)
        env.generate(scope="build")

        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_DOCS"] = False
        tc.cache_variables["BUILD_EXAMPLES"] = False
        # INFO: replace requires could be used to consume Qt 5.x
        tc.cache_variables["USE_QT6"] = self.dependencies["qt"].ref.version.major == "6"
        if self.settings.os in ["Macos", "iOS"]:
            # TODO: Remove after fixing https://github.com/conan-io/conan-center-index/issues/26005
            tc.extra_sharedlinkflags = ["-framework Metal"]
        tc.generate()

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
        self.cpp_info.requires = ["qt::qtCore", "qt::qtGui", "qt::qtWidgets", "qt::qtOpenGL"]
        self.cpp_info.set_property("cmake_file_name", "QtNodes")
        self.cpp_info.set_property("cmake_target_name", "QtNodes::QtNodes")
        self.cpp_info.defines = ["NODE_EDITOR_SHARED"] if self.options.shared else ["NODE_EDITOR_STATIC"]
        if self.settings.os in ["Macos", "iOS"]:
            # TODO: Remove after fixing https://github.com/conan-io/conan-center-index/issues/26005
            self.cpp_info.frameworks = ["Metal"]
