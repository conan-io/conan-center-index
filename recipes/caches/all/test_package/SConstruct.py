import os
from SCons.Environment import Environment
from SCons.Script import SConscript

flags = SConscript("SConscript_conandeps")
env = Environment(CXXFLAGS=["-std=c++11"], LIBS=["gtest"])

for package in ["conandeps", "gtest"]:
    env.MergeFlags(flags[package])

if not os.path.exists("dist"):
    os.mkdir("dist")

tests = env.Program(
    "./dist/tests",
    ["test.cpp"],
)

test = env.Alias(
    "test",
    [tests],
    "./dist/tests --gtest_brief",
)

env.AlwaysBuild(test)
