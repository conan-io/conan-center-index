import os
import textwrap

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, save


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualBuildEnv"
    test_type = "explicit"

    _cmake = None
    
    def _getOrCreateCMake(self):
        if self._cmake is None:
            self._cmake = CMake(self)
        return self._cmake
    
    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str, run=can_run(self))

    def build_requirements(self):
        if not can_run(self):
            self.tool_requires(self.tested_reference_str)

    def generate(self):
        qt_install_prefix = self.dependencies["qt"].package_folder.replace("\\", "/")
        qt_conf = textwrap.dedent(f"""\
            [Paths]
            Prefix = {qt_install_prefix}
            ArchData = bin/archdatadir
            HostData = bin/archdatadir
            Data = bin/datadir
            Sysconf = bin/sysconfdir
            LibraryExecutables = bin/archdatadir/bin
            Plugins = bin/archdatadir/plugins
            Imports = bin/archdatadir/imports
            Qml2Imports = bin/archdatadir/qml
            Translations = bin/datadir/translations
            Documentation = bin/datadir/doc
            Examples = bin/datadir/examples
        """)
        save(self, "qt.conf", qt_conf)

        VirtualRunEnv(self).generate()
        if can_run(self):
            VirtualRunEnv(self).generate(scope="build")


        qt_options = self.dependencies["qt"].options
        modules = ["Core"]
        if qt_options.with_dbus:
            modules.append("DBus")
        if qt_options.gui:
            modules.append("Gui")
        if qt_options.widgets:
            modules.append("Widgets")
        
        modules.append("Network")
        modules.append("Sql")
        modules.append("Test")
        if qt_options.get_safe("opengl", "no") != "no" and qt_options.gui:
            modules.append("OpenGL")
            
        modules.append("Concurrent")
        modules.append("Xml")

        if qt_options.qtdeclarative:
            modules.append("Qml")
#            modules.append("QmlModels")
            if qt_options.gui:
                modules.append("Quick")
                if qt_options.widgets:
                    modules.append("QuickWidgets")
#                modules.append("QuickShapes")
#            modules.append("QmlWorkerScript")
            modules.append("QuickTest")

        if qt_options.qttools and qt_options.gui and qt_options.widgets:
 #           modules.append("UiPlugin")
 #           modules.append("UiTools")
 #           if not cross_building(self):
 #               modules.append("Designer")
            modules.append("Help")

        if qt_options.qtquickcontrols2 and qt_options.gui:
            modules.append("QuickControls2")
#            modules.append("QuickTemplates2")

        if qt_options.qtsvg and qt_options.gui:
            modules.append("Svg")

#        if qt_options.qtwayland and qt_options.gui:
#            modules.append("WaylandClient")
#            modules.append("WaylandCompositor")

#        if qt_options.qtlocation:
#            modules.append("Positioning")
#            modules.append("Location")

        if qt_options.qtwebchannel:
            modules.append("WebChannel")

#        if qt_options.qtwebengine:
#            modules.append("WebEngineCore")
#            modules.append("WebEngine")
#            modules.append("WebEngineWidgets")

#        if qt_options.qtserialport:
#            modules.append("SerialPort")

#        if qt_options.qtserialbus:
#            modules.append("SerialBus")
#        if qt_options.qtsensors:
#            modules.append("Sensors")

#        if qt_options.qtscxml:
#            modules.append("Scxml")

#        if qt_options.qtpurchasing:
#            modules.append("Purchasing")

        if qt_options.qtcharts:
            modules.append("Charts")

#        if qt_options.qtgamepad:
#            modules.append("Gamepad")

        if qt_options.qt3d:
            modules.append("3DCore")
            modules.append("3DRender")
            modules.append("3DInput")
            modules.append("3DLogic")
            modules.append("3DExtras")
            modules.append("3DAnimation")

        if qt_options.qtmultimedia:
            modules.append("Multimedia")
            modules.append("MultimediaWidgets")
#            if qt_options.qtdeclarative and qt_options.gui:
#                modules.append("MultimediaQuick")
#            if qt_options.with_gstreamer:
#                modules.append("MultimediaGstTools")

        if qt_options.qtwebsockets:
            modules.append("WebSockets")

#        if qt_options.qtconnectivity:
#            modules.append("Bluetooth")
#            modules.append("Nfc")

#        if qt_options.qtdatavis3d:
#            modules.append("DataVisualization")

        if qt_options.qtnetworkauth:
            modules.append("NetworkAuth")

        if qt_options.get_safe("qtx11extras"):
            modules.append("X11Extras")

#        if qt_options.qtremoteobjects:
#            modules.append("RemoteObjects")

#        if qt_options.get_safe("qtwinextras"):
#            modules.append("WinExtras")

#        if qt_options.get_safe("qtmacextras"):
#            modules.append("MacExtras")

#        if qt_options.qtxmlpatterns:
#            modules.append("XmlPatterns")

#        if qt_options.get_safe("qtactiveqt"):
#            modules.append("AxBase")
#            modules.append("AxContainer")
#            modules.append("AxServer")

#        if qt_options.qtscript:
#            modules.append("Script")
#            if qt_options.widgets:
#                modules.append("ScriptTools")

#        if qt_options.qtandroidextras:
#            modules.append("AndroidExtras")

        if qt_options.qtwebview:
            modules.append("WebView")

#        if qt_options.qtvirtualkeyboard:
#            modules.append("VirtualKeyboard")

#        if qt_options.qtspeech:
#            modules.append("TextToSpeech")
            
        tc = CMakeToolchain(self)
        tc.variables["QT_MODULE"] = ";".join(modules)
        tc.variables["TEST_PACKAGE_QT_SHARED_LIBS"] = qt_options.shared
        
        tc.generate()
            
    def build(self):
        
        cmake = self._getOrCreateCMake()
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            copy(self, "qt.conf", src=self.generators_folder, dst=os.path.join(self.cpp.build.bindirs[0]))
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            cmake = self._getOrCreateCMake()
            cmake.test()
