from conan import ConanFile, conan_version
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.layout import basic_layout
import os
from io import StringIO


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        basic_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def build(self):
        pass
    
    @property
    def _version(self):
        if conan_version.major >= 2:
            return self.dependencies["perl"].ref.version
        else:
            return self.deps_cpp_info["perl"].version

    def test(self):
        if can_run(self):
            buffer = StringIO()
            # Magic syntax for getting the perl version: $^V
            # `perl --version` doesn't give a cleanly parsable output.
            self.run("perl -e 'print $^V'", buffer, env="conanrun")
            # Produces something like "v5.38.2"
            self.output.info(buffer.getvalue())
            if str(self._version) not in buffer.getvalue():
                raise ConanException(
                    f"perl reported wrong version. Expected {self._version}, got {buffer.getvalue()}."
                )
            
            self.run(f"perl {os.path.join(self.source_folder, 'test_package.pl')}", env="conanrun")

            # Check that the extensions requiring dependencies were built
            self.run("perl -e 'use IO::Compress::Bzip2'", env="conanrun")
            self.run("perl -e 'use Compress::Zlib'", env="conanrun")
