
import os
import subprocess
from conans import ConanFile, AutoToolsBuildEnvironment, tools, VisualStudioBuildEnvironment
from conans.tools import os_info, SystemPackageTool, download, untargz, replace_in_file
from conans.errors import ConanException


class ConanRecipe(ConanFile):
    name = "postgresql"
    vers = "14.3"
    version = vers + ".dssl1"
    settings = "os", "compiler", "build_type", "arch"
    description = "Conan package for the postgresql library"
    url = "https://github.com/trassir/conan-center-index"
    license = "https://www.postgresql.org/about/licence/"
    options = {"without_readline": [True, False],}
    default_options = "without_readline=False"
    exports_sources = ["pgdump_mute_warnings.patch"]
    version_v = "v" + vers

    @property
    def version_short(self):
        return self.version_v[1:]

    @property
    def pq_source_folder(self):
        return os.path.abspath('postgresql-{}'.format(self.version_short))

    @property
    def pq_msvc_dir(self):
        return os.path.join(self.pq_source_folder, 'src', 'tools', 'msvc')

    @property
    def pq_install_folder(self):
        return os.path.join(self.pq_source_folder, 'install_dir')

    def build_requirements(self):
        if self.settings.os == "Windows":
            try:
                self.run("perl -v")
            except ConanException:
                self.build_requires("strawberryperl/5.30.0.1")

        if os_info.is_linux and os_info.with_apt:
            if not self.options.without_readline:
                installer = SystemPackageTool()
                installer.install("libreadline-dev")

    def source(self):
        if self.version_v == 'master':
            raise NotImplementedError("Sources for master branch not implemented")
        else:
            url = "https://ftp.postgresql.org/pub/source/{}/postgresql-{}.tar.gz".format(self.version_v, self.version_short)
            zip_name = 'postgresql.tar.gz'
            download(url, zip_name)
            untargz(zip_name)
            os.unlink(zip_name)
            tools.patch(patch_file="pgdump_mute_warnings.patch", base_path=self.pq_source_folder)

    def build(self):
        if self.settings.os in ["Linux", "Macos"]:
            install_folder = self.pq_install_folder
            env = AutoToolsBuildEnvironment(self)
            with tools.environment_append(env.vars):
                with tools.chdir(self.pq_source_folder):
                    self.run("./configure --prefix={} && make".format(install_folder))
                    self.run("make install")

        elif self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                env = VisualStudioBuildEnvironment(self)
                with tools.environment_append(env.vars):
                    with tools.chdir(self.pq_msvc_dir):
                        vcvars = tools.vcvars_command(self)
                        self.run("{} && build.bat".format(vcvars))
            else:
                raise NotImplementedError("Windows compiler {!r} not implemented".format(str(self.settings.compiler)))
        else:
            raise NotImplementedError("Compiler {!r} for os {!r} not available".format(str(self.settings.compiler), str(self.settings.os)))

    def package(self):
        install_folder = self.pq_install_folder

        if self.settings.os == "Windows":
            install_pl = os.path.join(self.pq_msvc_dir, 'install.pl')
            replace_in_file(install_pl, "use Install qw(Install);", "use FindBin qw( $RealBin );\nuse lib $RealBin;\nuse Install qw(Install);")
            with tools.chdir(os.path.abspath(self.pq_msvc_dir)):
                self.run("install %s" % install_folder)

        self.copy("*", dst="", src=install_folder, keep_path=True)
        self.copy("*.py", dst="", keep_path=True)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["libpq",]
        else:
            self.cpp_info.libs = ["pq", ]
