import os
import stat
import glob
import shutil
import json
from conans import ConanFile, AutoToolsBuildEnvironment, tools

# based on https://github.com/conan-community/conan-ncurses/blob/stable/6.1/conanfile.py
class SipConan(ConanFile):
    name = "sip"
    version = "4.19.3"
    license = "GPL2"
    homepage = "https://www.riverbankcomputing.com/software/sip/intro"
    description = "SIP comprises a code generator and a Python module"
    url = "https://www.riverbankcomputing.com/hg/sip"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "python": ['python2', 'python3'],
    }
    default_options = {
        "python": "python2",
    }
    exports = ""
    _source_subfolder = "source_subfolder"

    def system_requirements(self):
        import pip
        if hasattr(pip, "main"):
            pip.main(["install", "mercurial"])
        else:
            from pip._internal import main as sipmain
            sipmain(['install', "mercurial"])
        if tools.os_info.is_windows:
            installer = tools.SystemPackageTool(tool=tools.ChocolateyTool())
            installer.install("winflexbison3")
        if tools.os_info.is_macos:
            installer = tools.SystemPackageTool(tool=tools.BrewTool())
            installer.install("bison")
            installer.install("flex")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        self.run("hg clone {url} {folder}".format(url = self.url, folder = self._source_subfolder))
        with tools.chdir(self._source_subfolder):
            self.run("hg up -C -r {rev}".format(rev = self.version))
        if tools.os_info.is_windows:
            tools.replace_in_file(os.path.join(self._source_subfolder, "build.py"),
                                  "os.system('flex -o%s %s' % (lexer_c, lexer_l))",
                                  "os.system('win_flex -o%s %s' % (lexer_c, lexer_l))")
            tools.replace_in_file(os.path.join(self._source_subfolder, "build.py"),
                                  "os.system('bison -y -d -o %s %s' % (parser_c, parser_y))",
                                  "os.system('win_bison -y -d -o %s %s' % (parser_c, parser_y))")

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("{python} build.py prepare".format(python = self.options.python))
            if tools.os_info.is_macos:
                self.run(("{python} configure.py"
                      + " --deployment-target=10.12"
                      + " -b {prefix}/bin"
                      + " -d {prefix}/lib-dynload"
                      + " -e {prefix}/include"
                      + " -v {prefix}/share/sip"
                ).format(
                    prefix = tools.unix_path(self.package_folder),
                    python = self.options.python
                ))
                self.run("make -j%d" % tools.cpu_count())
            if tools.os_info.is_windows:
                self.run(("{python} configure.py"
                      + " -b {prefix}/bin"
                      + " -d {prefix}/site-packages"
                      + " -e {prefix}/include"
                      + " -v {prefix}/share/sip"
                ).format(
                    prefix = self.package_folder,
                    python = self.options.python
                ))
                # cannot be bothered to fix build of siplib which we don't use anyway
                vcvarsall_cmd = tools.vcvars_command(self)
                with tools.chdir("sipgen"):
                    self.run("{vcv} && nmake".format(vcv=vcvarsall_cmd))

    def package(self):
        if tools.os_info.is_macos:
            with tools.chdir(self._source_subfolder):
                self.run("make install")
        if tools.os_info.is_windows:
            with tools.chdir(self._source_subfolder):
                # partial execution of installation step due to siplib not being built
                with tools.chdir("sipgen"):
                    vcvarsall_cmd = tools.vcvars_command(self)
                    self.run("{vcv} && nmake install".format(vcv=vcvarsall_cmd))
                with tools.chdir("siplib"):
                    self.run("mkdir {prefix}\\include\\".format(prefix = self.package_folder))
                    self.run("copy /y sip.h {prefix}\\include\\sip.h".format(prefix = self.package_folder))

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ["include"]
        if tools.os_info.is_macos:
            self.cpp_info.libdirs = ["lib-dynload"]
