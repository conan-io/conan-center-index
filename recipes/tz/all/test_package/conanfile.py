from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.layout import basic_layout


class TzTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    apply_env = False

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        basic_layout()

    def test(self):
        if not cross_building(self):
            if not self.dependencies["tz"].options.data_only:
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
