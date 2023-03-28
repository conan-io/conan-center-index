import os
from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.files import copy, get
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.58.0"


class NodejsConan(ConanFile):
    name = "nodejs"
    description = "nodejs binaries for use in recipes"
    topics = ("node", "nodejs")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nodejs.org"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    short_paths = True

    min_gcc_version = '8.3'
    min_clang_version = '11.0'
    min_apple_clang_version = '11.0.0'
    min_msvc_version = '19.28'

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    @property
    def _nodejs_arch(self):
        if str(self.settings.os) == "Linux":
            if str(self.settings.arch).startswith("armv7"):
                return "armv7"
            if str(self.settings.arch).startswith("armv8") and "32" not in str(self.settings.arch):
                return "armv8"
        return str(self.settings.arch)

    def validate(self):
        if not self.version in self.conan_data["sources"] or \
           not str(self.settings.os) in self.conan_data["sources"][self.version] or \
           not self._nodejs_arch in self.conan_data["sources"][self.version][str(self.settings.os)]:
            raise ConanInvalidConfiguration("Binaries for this combination of architecture/version/os not available")

        building_doc_url = "https://github.com/nodejs/node/blob/v{}/BUILDING.md".format(str(self.version))
        if Version(str(self.version)) >= '18.0.0':
            if self.settings.os in ('Linux', 'Macos'):
                if self.settings.compiler == 'gcc' and Version(str(self.settings.compiler.version)) < self.min_gcc_version:
                    raise ConanInvalidConfiguration('GCC must be >= %s (read the doc: %s)' % (self.min_gcc_version, building_doc_url))
                if self.settings.compiler == 'clang' and Version(str(self.settings.compiler.version)) < self.min_clang_version:
                    raise ConanInvalidConfiguration('Clang must be >= %s (read the doc: %s)' % (self.min_clang_version, building_doc_url))
                if self.settings.compiler == 'apple-clang' and Version(str(self.settings.compiler.version)) < self.min_apple_clang_version:
                    raise ConanInvalidConfiguration('Apple-Clang must be >= %s (read the doc: %s)' % (self.min_apple_clang_version, building_doc_url))

                if self.settings.compiler != 'apple-clang':
                    if self.settings.compiler.libcxx != 'libstdc++11':
                        raise ConanInvalidConfiguration('Only libstdc++11 is supported (read the doc: %s)' % (building_doc_url))
            elif self.settings.os is 'Windows':
                if self.settings.compiler == 'msvc' and Version(str(self.settings.compiler.version)) < self.min_msvc_version:
                    raise ConanInvalidConfiguration('GCC must be >= %s (read the doc: %s)' % (self.min_msvc_version, building_doc_url))
            else:
                raise ConanInvalidConfiguration("Profile not supported")

    def build(self):
        get(self, **self.conan_data["sources"][self.version][str(self.settings.os)][self._nodejs_arch], destination=self._source_subfolder, strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        if Version(str(self.version)) < '18.0.0':
            copy(self, pattern="*", src=os.path.join(self._source_subfolder, "bin"), dst="bin")
            copy(self, pattern="node.exe", src=self._source_subfolder, dst="bin")
            copy(self, pattern="npm", src=self._source_subfolder, dst="bin")
            copy(self, pattern="npx", src=self._source_subfolder, dst="bin")
        else:
            copy(self, pattern="*", src=os.path.join(self._source_subfolder, "bin"), dst="bin", keep_path=True)
            copy(self, pattern="*", src=os.path.join(self._source_subfolder, "lib"), dst="lib", keep_path=True)

    def package_info(self):
        self.cpp_info.includedirs = []
        bin_dir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bin_dir))
        self.env_info.PATH.append(bin_dir)
