from conans import ConanFile, tools, MSBuild
import os

class PegConan(ConanFile):
    name = "peg"
    license = "MIT"
    description = "peg and leg are tools for generating recursive-descent parsers"
    topics = ("conan", "peg", "leg", "parser")
    homepage = "https://www.piumarta.com/software/peg/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "bin"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        if self.settings.os == "Windows":
            with tools.chdir(self._source_subfolder):
                with tools.vcvars(self.settings):
                    msbuild = MSBuild(self)
                    if self.settings.arch == "x86":
                        msbuild.build_env.link_flags.append("/MACHINE:X86")
                    elif self.settings.arch == "x86_64":
                        msbuild.build_env.link_flags.append("/SAFESEH:NO /MACHINE:X64")
                    msbuild.build(project_file="peg.sln", platforms={"x86": "Win32"}, build_type="Release", force_vcvars=True, arch="x86")
        else:
            os.chdir(self._source_subfolder)
            self.run("make")

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Windows":
            self.copy("*.exe")
        else:
            self.copy(os.path.join(self._source_subfolder, "peg"))
            self.copy(os.path.join(self._source_subfolder, "leg"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: %s" % bin_path)
        self.env_info.PATH.append(bin_path)
