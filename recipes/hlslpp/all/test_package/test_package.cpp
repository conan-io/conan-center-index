#include <hlsl++.h>

int main() {
  hlslpp::float4 foo4 = hlslpp::float4(1, 2, 3, 4);
  hlslpp::float3 bar3 = foo4.xzy;
  hlslpp::float2 logFoo2 = hlslpp::log(bar3.xz);
  foo4.wx = logFoo2.yx;
  hlslpp::float4 baz4 = hlslpp::float4(logFoo2, foo4.zz);
  hlslpp::float4x4 fooMatrix4x4 = hlslpp::float4x4(1, 2, 3, 4,
                                                   5, 6, 7, 8,
                                                   8, 7, 6, 5,
                                                   4, 3, 2, 1);
  hlslpp::float4 myTransformedVector = hlslpp::mul(fooMatrix4x4, baz4);
  hlslpp::int2 ifoo2 = hlslpp::int2(1, 2);
  hlslpp::int4 ifoo4 = hlslpp::int4(1, 2, 3, 4) + ifoo2.xyxy;

  return 0;
}
