#include <asmjit/x86.h>
#include <stdio.h>

using namespace asmjit;

// Signature of the generated function.
typedef int (*Func)(void);

int main() {
  JitRuntime rt;                           // Runtime specialized for JIT code execution.
  CodeHolder code;                         // Holds code and relocation information.

  code.init(rt.environment(),              // Initialize code to match the JIT environment.
            rt.cpuFeatures());
  x86::Compiler cc(&code);                 // Create and attach x86::Compiler to code.

  cc.addFunc(FuncSignature::build<int>()); // Begin a function of `int fn(void)` signature.

  x86::Gp vReg = cc.newGpd();              // Create a 32-bit general purpose register.
  cc.mov(vReg, 1);                         // Move one to our virtual register `vReg`.
  cc.ret(vReg);                            // Return `vReg` from the function.

  cc.endFunc();                            // End of the function body.
  cc.finalize();                           // Translate and assemble the whole 'cc' content.
  // ----> x86::Compiler is no longer needed from here and can be destroyed <----

  Func fn;
  Error err = rt.add(&fn, &code);          // Add the generated code to the runtime.
  if (err) return 1;                       // Handle a possible error returned by AsmJit.
  // ----> CodeHolder is no longer needed from here and can be destroyed <----

  int result = fn();                       // Execute the generated code.
  printf("%d\n", result);                  // Print the resulting "1".

  rt.release(fn);                          // Explicitly remove the function from the runtime.
  return 0;
}
