from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get

import os
import sys

required_conan_version = ">=1.53"

class ProtobufPythonPkg(ConanFile):
    name = "protobuf-python"
    description = "Protocol Buffers - Google's data interchange format - Python Module"
    topics = ("protocol-buffers", "protocol-compiler", "serialization", "rpc", "protocol-compiler", "python")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/protocolbuffers/protobuf"
    license = "BSD-3-Clause"

    def layout(self):
        basic_layout(self,src_folder="src")

    def requirements(self):
        self.requires(f"protobuf/{self.version}", run=True, build=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        self.run(f"{sys.executable} setup.py build",
                 cwd=os.path.join(self.source_folder, "python"))

    @property
    def _python_instdir(self):
        return "lib/python/site-packages"

    def package(self):
        copy(self, "*",
             os.path.join(self.source_folder, "python", "build", "lib"),
             os.path.join(self.package_folder, self._python_instdir))

    def package_info(self):
        self.buildenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, self._python_instdir))
        self.runenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, self._python_instdir))

    def package_id(self):
        self.info.clear()
