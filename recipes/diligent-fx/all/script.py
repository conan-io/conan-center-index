# ----------------------------------------------------------------------------
# Copyright 2019-2022 Diligent Graphics LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# In no event and under no legal theory, whether in tort (including negligence),
# contract, or otherwise, unless required by applicable law (such as deliberate
# and grossly negligent acts) or agreed to in writing, shall any Contributor be
# liable for any damages, including any direct, indirect, special, incidental,
# or consequential damages of any character arising as a result of this License or
# out of the use or inability to use the software (including but not limited to damages
# for loss of goodwill, work stoppage, computer failure or malfunction, or any and
# all other commercial damages or losses), even if such Contributor has been advised
# of the possibility of such damages.
# ----------------------------------------------------------------------------

import sys


def main():
    try:
        if len(sys.argv) < 3:
            raise ValueError("Incorrect number of command line arguments. Expected arguments: src file, dst file")

        if sys.argv[1] == sys.argv[2]:
            raise ValueError("Source and destination files must be different")

        with open(sys.argv[1], "r") as src_file, open(sys.argv[2], "w") as dst_file:
            special_chars = "\'\"\\"

            for line in src_file:
                dst_file.write('\"')

                for i, c in enumerate(line.rstrip()):
                    if special_chars.find(c) != -1:
                        dst_file.write('\\')
                    dst_file.write(c)

                dst_file.write('\\n\"\n')

        print("File2String: successfully converted {} to {}".format(sys.argv[1], sys.argv[2]))
    except (ValueError, IOError) as error:
        print(error)
        sys.exit(1)


if __name__ == "__main__":
    main()
