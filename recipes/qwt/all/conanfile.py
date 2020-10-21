import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

class QwtConan(ConanFile):
    name = "qwt"
    license = "Qwt License, Version 1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://qwt.sourceforge.io/"
    topics = ("conan", "archive", "compression")
    description = (
        "The Qwt library contains GUI Components and utility classes which are primarily useful for programs "
        "with a technical background. Beside a framework for 2D plots it provides scales, sliders, dials, compasses, "
        "thermometers, wheels and knobs to control or display values, arrays, or ranges of type double."
    )
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "plot": [True, False],
        "widgets": [True, False],
        "svg": [True, False],
        "opengl": [True, False],
        "mathml": [True, False],
        "designer": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "plot": True,
        "widgets": True,
        "opengl": True,
        "designer": True,
        "mathml": False,
        "svg": False

    }
    generators = "qmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("qt/5.15.1")

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            raise ConanInvalidConfiguration("Only msvc compiler is supported on windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("qwt-{}".format(self.version), self._source_subfolder)

    def _patch_qwt_config_files(self):
        ## qwtconfig.pri ##
        qwtconfig_path = os.path.join(self.source_folder, self._source_subfolder, "qwtconfig.pri")
        qwtconfig = tools.load(qwtconfig_path)

        qwtconfig = "CONFIG += conan_basic_setup\ninclude(../conanbuildinfo.pri)\n" + qwtconfig
        qwtconfig += "QWT_CONFIG {}= QwtDll\n".format("+" if self.options.shared else "-")
        qwtconfig += "QWT_CONFIG {}= QwtPlot\n".format("+" if self.options.plot else "-")
        qwtconfig += "QWT_CONFIG {}= QwtWidgets\n".format("+" if self.options.widgets else "-")
        qwtconfig += "QWT_CONFIG {}= QwtSvg\n".format("+" if self.options.svg else "-")
        qwtconfig += "QWT_CONFIG {}= QwtOpenGL\n".format("+" if self.options.opengl else "-")
        qwtconfig += "QWT_CONFIG {}= QwtMathML\n".format("+" if self.options.mathml else "-")
        qwtconfig += "QWT_CONFIG {}= QwtDesigner\n".format("+" if self.options.designer else "-")
        tools.save(qwtconfig_path, qwtconfig)

        ## qwtbuild.pri ##
        qwtbuild_path = os.path.join(self.source_folder, self._source_subfolder, "qwtbuild.pri")
        qwtbuild = tools.load(qwtbuild_path)
        # set build type
        qwtbuild += "CONFIG -= debug_and_release\n"
        qwtbuild += "CONFIG -= build_all\n"
        qwtbuild += "CONFIG -= release\n"
        qwtbuild += "CONFIG += {}\n".format("debug" if self.settings.build_type=="Debug" else "release")
        tools.save(qwtbuild_path, qwtbuild)


    def build(self):
        self._patch_qwt_config_files()

        if self.settings.os == "Windows":
            vcvars = tools.vcvars_command(self.settings)
            self.run("{} && qmake {}".format(vcvars, self._source_subfolder), run_environment=True)
            self.run("{} && nmake".format(vcvars))
        else:
            self.run("qmake {}".format(self._source_subfolder), run_environment=True)
            self.run("make -j {}".format(tools.cpu_count()))


    def package(self):
        self.copy("COPYING", src=os.path.join(self._source_subfolder), dst="licenses")
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "src"))
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.so*", dst="lib", keep_path=False, symlinks=True)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = ['include']
        self.cpp_info.libs = ["qwtd"] if self.settings.build_type=="Debug" else ["qwt"]
        self.env_info.QT_PLUGIN_PATH.append(os.path.join(self.package_folder, 'bin'))
        self.env_info.QT_PLUGIN_PATH.append(os.path.join(self.package_folder, 'lib'))
