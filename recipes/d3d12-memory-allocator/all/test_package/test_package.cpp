#include <D3D12MemAlloc.h>
#include <d3d12.h>

int main() {
  D3D12_RESOURCE_DESC resourceDesc = {};
  resourceDesc.Dimension = D3D12_RESOURCE_DIMENSION_TEXTURE2D;
  resourceDesc.Alignment = 0;
  resourceDesc.Width = 1024;
  resourceDesc.Height = 1024;
  resourceDesc.DepthOrArraySize = 1;
  resourceDesc.MipLevels = 1;
  resourceDesc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
  resourceDesc.SampleDesc.Count = 1;
  resourceDesc.SampleDesc.Quality = 0;
  resourceDesc.Layout = D3D12_TEXTURE_LAYOUT_UNKNOWN;
  resourceDesc.Flags = D3D12_RESOURCE_FLAG_NONE;

  D3D12MA::ALLOCATION_DESC allocDesc = {};
  allocDesc.HeapType = D3D12_HEAP_TYPE_DEFAULT;

  D3D12Resource *resource;
  D3D12MA::Allocation *allocation;
  HRESULT hr = allocator->CreateResource(&allocDesc, &resourceDesc,
                                         D3D12_RESOURCE_STATE_COPY_DEST, NULL,
                                         &allocation, IID_PPV_ARGS(&resource));

  return 0;
}
