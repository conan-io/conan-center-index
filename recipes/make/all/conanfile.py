from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os

required_conan_version = ">=1.33.0"


class MakeConan(ConanFile):
    name = "make"
    description = "GNU Make is a tool which controls the generation of executables and other non-source files of a program from the program's source files"
    topics = ("conan", "make", "build", "makefile")
    homepage = "https://www.gnu.org/software/make/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "patches/*"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package_id(self):
        del self.info.settings.compiler

    def build(self):
        for patch in self.conan_data.get("patches").get(self.version, []):
            tools.files.patch(self, **patch)

        with tools.files.chdir(self, self._source_subfolder):
            # README.W32
            if tools.os_info.is_windows:
                if self.settings.compiler == "Visual Studio":
                    command = "build_w32.bat --without-guile"
                else:
                    command = "build_w32.bat --without-guile gcc"
            else:
                env_build = AutoToolsBuildEnvironment(self)
                env_build.configure()
                command = "./build.sh"
            with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
                self.run(command)

    def package(self):
        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        self.copy(pattern="make", src=self._source_subfolder, dst="bin", keep_path=False)
        self.copy(pattern="*gnumake.exe", src=self._source_subfolder, dst="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = []

        make = os.path.join(self.package_folder, "bin", "gnumake.exe" if self.settings.os == "Windows" else "make")

        self.user_info.make = make

        self.output.info('Creating CONAN_MAKE_PROGRAM environment variable: %s' % make)
        self.env_info.CONAN_MAKE_PROGRAM = make
