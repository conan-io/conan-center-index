import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=1.33.0"


class AGSConan(ConanFile):
    name = "ags"
    description = "The AMD GPU Services (AGS) library provides software developers with the ability to query AMD GPU " \
                  "software and hardware state information that is not normally available through standard operating " \
                  "systems or graphics APIs."
    homepage = "https://github.com/GPUOpen-LibrariesAndSDKs/AGS_SDK"
    topics = ("conan", "amd", "gpu")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    license = "MIT"
    no_copy_source = True
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _supported_msvc_versions(self):
        return ["14", "15", "16"]

    @property
    def _supported_archs(self):
        return ["x86_64", "x86"]

    def configure(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("ags doesn't support OS: {}.".format(self.settings.os))
        if self.settings.compiler != "Visual Studio":
            raise ConanInvalidConfiguration("ags doesn't support compiler: {} on OS: {}.".
                                            format(self.settings.compiler, self.settings.os))

        if self.settings.compiler == "Visual Studio":
            if self.settings.compiler.version not in self._supported_msvc_versions:
                raise ConanInvalidConfiguration("ags doesn't support MSVC version: {}".format(self.settings.compiler.version))
            if self.settings.arch not in self._supported_archs:
                raise ConanInvalidConfiguration("ags doesn't support arch: {}".format(self.settings.arch))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _convert_msvc_version_to_vs_version(self, msvc_version):
        vs_versions = {
            "14": "2015",
            "15": "2017",
            "16": "2019",
        }
        return vs_versions.get(str(msvc_version), None)

    def _convert_arch_to_win_arch(self, msvc_version):
        vs_versions = {
            "x86_64": "x64",
            "x86": "x86",
        }
        return vs_versions.get(str(msvc_version), None)

    def package(self):
        ags_lib_path = os.path.join(self.source_folder, self._source_subfolder, "ags_lib")
        self.copy("LICENSE.txt", dst="licenses", src=ags_lib_path)
        self.copy("*.h", dst="include", src=os.path.join(ags_lib_path, "inc"))

        if self.settings.compiler == "Visual Studio":
            win_arch = self._convert_arch_to_win_arch(self.settings.arch)
            if self.options.shared:
                shared_lib = "amd_ags_{arch}.dll".format(arch=win_arch)
                symbol_lib = "amd_ags_{arch}.lib".format(arch=win_arch)
                self.copy(shared_lib, dst="bin", src=os.path.join(ags_lib_path, "lib"))
                self.copy(symbol_lib, dst="lib", src=os.path.join(ags_lib_path, "lib"))
            else:
                vs_version = self._convert_msvc_version_to_vs_version(self.settings.compiler.version)
                static_lib = "amd_ags_{arch}_{vs_version}_{runtime}.lib".format(arch=win_arch, vs_version=vs_version, runtime=self.settings.compiler.runtime)
                self.copy(static_lib, dst="lib", src=os.path.join(ags_lib_path, "lib"))

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self, self)
