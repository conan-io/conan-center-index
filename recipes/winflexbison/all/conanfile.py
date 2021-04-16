import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class WinflexbisonConan(ConanFile):
    name = "winflexbison"
    description = "Flex and Bison for Windows"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lexxmark/winflexbison"
    topics = ("conan", "winflexbison", "flex", "bison")

    generators = "cmake"
    license = "GPL-3.0-or-later"
    exports_sources = ["CMakeLists.txt"]

    settings = "os", "build_type", "arch", "compiler"

    _source_subfolder = "source_subfolder"

    _cmake = None

    def config_options(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("winflexbison is only supported on Windows.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
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
            self.copy(pattern="*.exe", dst="bin", src=actual_build_path, keep_path=False)
        else:
            self.copy(pattern="*.exe", dst="bin", src="bin", keep_path=False)
        self.copy(pattern="data/*", dst="bin", src="{}/bison".format(self._source_subfolder), keep_path=True)
        self.copy(pattern="FlexLexer.h", dst="include", src=os.path.join(self._source_subfolder, "flex", "src"), keep_path=False)

        # Copy licenses
        self._extract_license()
        self.copy(pattern="COPYING.GPL3", dst="licenses")
        self.copy(pattern="COPYING", dst="licenses", src=os.path.join(self._source_subfolder, "flex", "src"), keep_path=False)
        os.rename(os.path.join(self.package_folder, "licenses", "COPYING"), os.path.join(self.package_folder, "licenses", "bison-license"))
        self.copy(pattern="COPYING", dst="licenses", src=os.path.join(self._source_subfolder, "bison", "src"), keep_path=False)
        os.rename(os.path.join(self.package_folder, "licenses", "COPYING"), os.path.join(self.package_folder, "licenses", "flex-license"))

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
