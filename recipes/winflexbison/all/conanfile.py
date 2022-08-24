from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">= 1.33.0"


class WinflexbisonConan(ConanFile):
    name = "winflexbison"
    description = "Flex and Bison for Windows"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lexxmark/winflexbison"
    topics = ("flex", "bison")
    generators = "cmake"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "CMakeLists.txt", "patches/*"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("winflexbison is only supported on Windows.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_license(self):
        with open(os.path.join(self._source_subfolder, "bison", "data", "skeletons", "glr.cc")) as f:
            content_lines = f.readlines()
        license_content = []
        for i in range(2, 16):
            license_content.append(content_lines[i][2:-1])
        tools.save("COPYING.GPL3", "\n".join(license_content))

    def package(self):
        if self.settings.build_type in ("Release", "Debug") and tools.Version(self.version) < "2.5.23":
            actual_build_path = "{0}/bin/{1}".format(self._source_subfolder, self.settings.build_type)
            self.copy("*.exe", src=actual_build_path, dst="bin", keep_path=False)
        else:
            self.copy("*.exe", src="bin", dst="bin", keep_path=False)
        self.copy("data/*", src="{}/bison".format(self._source_subfolder), dst="bin", keep_path=True)
        self.copy("FlexLexer.h", src=os.path.join(self._source_subfolder, "flex", "src"), dst="include", keep_path=False)

        # Copy licenses
        self._extract_license()
        self.copy("COPYING.GPL3", dst="licenses")
        self.copy("COPYING", src=os.path.join(self._source_subfolder, "flex", "src"), dst="licenses", keep_path=False)
        tools.rename(os.path.join(self.package_folder, "licenses", "COPYING"), os.path.join(self.package_folder, "licenses", "bison-license"))
        self.copy("COPYING", src=os.path.join(self._source_subfolder, "bison", "src"), dst="licenses", keep_path=False)
        tools.rename(os.path.join(self.package_folder, "licenses", "COPYING"), os.path.join(self.package_folder, "licenses", "flex-license"))

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        lex_path = os.path.join(self.package_folder, "bin", "win_flex").replace("\\", "/")
        self.output.info("Setting LEX environment variable: {}".format(lex_path))
        self.env_info.LEX = lex_path

        yacc_path = os.path.join(self.package_folder, "bin", "win_bison -y").replace("\\", "/")
        self.output.info("Setting YACC environment variable: {}".format(yacc_path))
        self.env_info.YACC = yacc_path
