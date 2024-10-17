#include <webgpu/webgpu_cpp.h>

int main() {
    wgpu::InstanceDescriptor instanceDescriptor{};
    wgpu::Instance instance = wgpu::CreateInstance(&instanceDescriptor);
}
