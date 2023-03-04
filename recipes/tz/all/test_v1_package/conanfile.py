import os

from conan import ConanFile
from conan.tools.build import cross_building

required_conan_version = "<2.0.0"

class TzTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    apply_env = False
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if not cross_building(self):
            if not self.options["tz"].data_only:
                which = "where" if self.settings.os == "Windows" else "which"
                cmd = f"{which} zdump"
                self.output.info(f"Executing '{cmd}'")
                self.run(cmd, env="conanrun")

                cmd = "zdump -v America/Los_Angeles"
                self.output.info(f"Executing '{cmd}'")
                self.run(cmd, env="conanrun")

            self.output.info("Test that tzdata is readable")
            cmd = "python -c 'import os; tzdata = os.environ[\"TZDATA\"]; f=open(os.path.join(tzdata, \"factory\"), \"r\"); s = f.read(); f.close(); print(s)'"
            self.run(cmd, env="conanrun")
