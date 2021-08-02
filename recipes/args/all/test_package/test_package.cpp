#include <args.hxx>

#include <iostream>

int main(int argc, char *argv[]) {
  args::ArgumentParser parser("test_package");

  args::Positional<int> arg{parser, "arg",
                            "display the square of the given integer"};

  try {
    parser.ParseCLI(argc, argv);
  } catch (const args::Error &e) {
    std::cout << e.what() << std::endl;
    return 1;
  }

  int input = arg.Get();
  std::cout << (input * input) << std::endl;

  return 0;
}
