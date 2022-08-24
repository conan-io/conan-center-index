from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.40.0"


class ConanXqilla(ConanFile):
    name = "xsd"
    
    description = (
        "XSD is a W3C XML Schema to C++ translator. It generates vocabulary-specific, statically-typed C++ mappings (also called bindings) from XML Schema definitions. XSD supports two C++ mappings: in-memory C++/Tree and event-driven C++/Parser."
    )
    topics = ("xsd", "xml", "c++")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://codesynthesis.com/projects/xsd/"
    license = ("GPL-2.0","FLOSSE")
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("xerces-c/3.2.3")

    @property
    def _doc_folder(self):
        return os.path.join(self._source_subfolder,"xsd","doc")

    @property
    def _make_cmd(self):
        return self._gnumake_cmd

    @property
    def _make_program(self):
        return tools.get_env('CONAN_MAKE_PROGRAM', tools.which('make'))
    
    @property
    def _gnumake_cmd(self):
        make_ldflags = "LDFLAGS='{libs} -pthread'".format(
            libs=" ".join(["-L{}".format(os.path.join(self.deps_cpp_info["xerces-c"].rootpath, it)) for it in self.deps_cpp_info["xerces-c"].libdirs]))
        flags = []
        flags.append(' '.join(["-I{}".format(os.path.join(self.deps_cpp_info["xerces-c"].rootpath, it)) for it in self.deps_cpp_info["xerces-c"].includedirs]))
        if self.settings.compiler == "gcc":
            flags.append('-std=c++11')
        make_ccpflags = "CPPFLAGS='{}'".format(" ".join(flags))
        make_cmd = f'{make_ldflags} {make_ccpflags} {self._make_program} -j{tools.cpu_count()}'
        return make_cmd

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("The xsd recipe currently only supports Linux.")
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
       
        with tools.files.chdir(self, self._source_subfolder):
                self.run(self._make_cmd)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=os.path.join(self._source_subfolder, "xsd"))
        self.copy("GPLv2", dst="licenses", src=os.path.join(self._source_subfolder, "xsd"))
        self.copy("FLOSSE", dst="licenses", src=os.path.join(self._source_subfolder, "xsd"))

        with tools.files.chdir(self, self._source_subfolder):
            self.run(self._make_install_cmd)
        
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.path.append(bin_path)

    @property
    def _make_install_cmd(self):
        make_install_cmd = f'{self._make_cmd} install_prefix={self.package_folder} install'
        return make_install_cmd
