from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class MakeConan(ConanFile):
    name = "make"
    description = "GNU Make is a tool which controls the generation of executables and other non-source files of a program from the program's source files"
    topics = ("conan", "make", "build", "makefile")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/make/"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["patches/*"]
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "make-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def package_id(self):
        del self.info.settings.compiler

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        with tools.chdir(self._source_subfolder):
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
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="make", dst="bin", src=self._source_subfolder, keep_path=False)
        self.copy(pattern="*gnumake.exe", dst="bin", src=self._source_subfolder, keep_path=False)

    def package_info(self):
        make = "gnumake.exe" if self.settings.os == "Windows" else "make"
        make = os.path.join(self.package_folder, "bin", make)
        self.output.info('Creating CONAN_MAKE_PROGRAM environment variable: %s' % make)
        self.env_info.CONAN_MAKE_PROGRAM = make
