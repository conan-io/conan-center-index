import os
from conans import ConanFile, tools
from conan.tools.files import get
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.58.0"


class NodejsConan(ConanFile):
    name = "nodejs"
    description = "nodejs binaries for use in recipes"
    topics = ("conan", "node", "nodejs")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nodejs/node"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = False

    def validate(self):
        if self.version.as_list[0] >= 18:
            if self.settings.os == 'Linux' and self.settings.compiler == 'gcc' and tools.Version(str(self.settings.compiler.version)) < '8.0':
                raise ConanInvalidConfiguration('GCC must be >= 8.0')

    def build_requirements(self):
        self.tool_requires("ninja/1.10.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        self.run('./configure --ninja && make', run_environment=True)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_folder)
        self.copy(pattern="*", src=os.path.join(self.source_folder, "bin"), dst="bin", symlinks=True, keep_path=True)
        self.copy(pattern="*", src=os.path.join(self.source_folder, "lib"), dst="lib", symlinks=True, keep_path=True)

    def package_info(self):
        self.cpp_info.includedirs = []
        bin_dir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bin_dir))
        self.env_info.PATH.append(bin_dir)
