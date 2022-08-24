from conan import ConanFile, tools
from conans import CMake
import os


class JwasmConan(ConanFile):
    name = "jwasm"
    description = "JWasm is intended to be a free Masm-compatible assembler."
    license = "Watcom-1.0"
    topics = ("conan", "jwasm", "masm", "assembler")
    homepage = "https://github.com/JWasm/JWasm"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("JWasm-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              'string(REPLACE "/MD" "/MT" ${CompilerFlag} "${${CompilerFlag}}")',
                              "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("License.txt", dst="licenses", src=self._source_subfolder)
        suffix = ".exe" if self.settings.os == "Windows" else ""
        self.copy("jwasm" + suffix, dst="bin", src="bin")

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
