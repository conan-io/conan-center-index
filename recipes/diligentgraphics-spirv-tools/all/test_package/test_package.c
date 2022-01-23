#include "spirv-tools/libspirv.h"

int main(int argc, char ** argv)
{
const char input_text[] =
    "OpCapability Shader\n"
    "OpCapability Linkage\n"
    "OpMemoryModel Logical GLSL450";
  spv_text text;
  spv_binary binary;
  spv_context context;

  context  = spvContextCreate(SPV_ENV_UNIVERSAL_1_1);

  binary = 0;
  if( SPV_SUCCESS != spvTextToBinary(context, input_text, sizeof(input_text), &binary, 0) )
  {
      return 1;
  }

  text = 0;
  if( SPV_SUCCESS != spvBinaryToText(context, binary->code, binary->wordCount, 0, &text, 0) )
  {
      return 1;
  }

  spvTextDestroy(text);
  spvBinaryDestroy(binary);
  spvContextDestroy(context);
  return 0;
}
