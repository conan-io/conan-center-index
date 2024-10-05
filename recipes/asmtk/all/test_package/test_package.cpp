#include <asmjit/asmjit.h>
#include <asmtk/asmtk.h>



// Used to print binary code as hex.
static void dumpCode(const uint8_t* buf, size_t size) {
  constexpr uint32_t kCharsPerLine = 39;
  char hex[kCharsPerLine * 2 + 1];

  size_t i = 0;
  while (i < size) {
    size_t j = 0;
    size_t end = size - i < kCharsPerLine ? size - i : size_t(kCharsPerLine);

    end += i;
    while (i < end) {
      uint8_t b0 = buf[i] >> 4;
      uint8_t b1 = buf[i] & 15;

      hex[j++] = b0 < 10 ? '0' + b0 : 'A' + b0 - 10;
      hex[j++] = b1 < 10 ? '0' + b1 : 'A' + b1 - 10;
      i++;
    }

    hex[j] = '\0';
    puts(hex);
  }
}

int main(int argc, char* argv[]) {
  using namespace asmjit;
  using namespace asmtk;
  // Setup CodeHolder for X64.
  Environment env(Arch::kX64);
  CodeHolder code;
  code.init(env);

  // Attach x86::Assembler to `code`.
  x86::Assembler a(&code);

  // Create AsmParser that will emit to x86::Assembler.
  AsmParser p(&a);

  // Parse some assembly.
  Error err = p.parse(
    "mov rax, rbx\n"
    "vaddpd zmm0, zmm1, [rax + 128]\n");

  // Error handling (use asmjit::ErrorHandler for more robust error handling).
  if (err) {
    printf("ERROR: %08x (%s)\n", err, DebugUtils::errorAsString(err));
    return 1;
  }

  // Now you can print the code, which is stored in the first section (.text).
  CodeBuffer& buffer = code.sectionById(0)->buffer();
  dumpCode(buffer.data(), buffer.size());

  return 0;
}