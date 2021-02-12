import os
from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools
from conans.errors import ConanInvalidConfiguration
from glob import glob


class TssMsrConan(ConanFile):
    name = "tssmsr"
    description = "TPM Software Stack (TSS) implementations from Microsoft"
    topics = ("tpm", "tss", "crypto", "microsoft")
    homepage = "https://github.com/microsoft/TSS.MSR"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "compiler", "arch", "build_type"
    generators = "make"
    exports_sources = "patches/*"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return os.path.join(self._source_subfolder, "TSS.CPP")

    @property
    def _minimum_cpp_standard(self):
        return 11

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "14",
            "gcc": "5",
            "clang": "3.9",
            "apple-clang": "8",
        }

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))

    def requirements(self):
        # VC builds link against openssl included in the sources
        if not self.settings.compiler == "Visual Studio":
            self.requires("openssl/1.1.1g")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob("TSS.MSR-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.settings.compiler == "Visual Studio":
            msbuild = MSBuild(self)
            msbuild.build(os.path.join(self._build_subfolder, "TSS.CPP.sln"), targets=["TSS_CPP"])
        else:
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make(
                args=[f"CONFIG={str(self.settings.build_type).lower()}", "-C", self._build_subfolder])

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        self.copy("*.h", dst="include",
                  src=os.path.join(self._build_subfolder, "include"))
        self.copy("**/libtss*.a", dst="lib", keep_path=False)
        self.copy("**/libtss*.so", dst="lib", keep_path=False)
        self.copy("**/TSS.CPP.dll", dst="bin", keep_path=False)
        self.copy("**/TSS.CPP.lib", dst="lib", keep_path=False)

    def package_info(self):
        if tools.os_info.is_windows:
            self.cpp_info.libs = ["tss.cpp"]
        else:
            self.cpp_info.libs = [
                "tss" + ("d" if self.settings.build_type == "Debug" else "")]
