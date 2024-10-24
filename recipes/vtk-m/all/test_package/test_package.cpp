#include <vtkm/cont/Initialize.h>
#include <vtkm/source/Tangle.h>

int main(int argc, char *argv[]) {
  vtkm::cont::Initialize(argc, argv, vtkm::cont::InitializeOptions::Strict);
  vtkm::source::Tangle tangle;
  tangle.SetPointDimensions({ 50, 50, 50 });
  vtkm::cont::DataSet tangleData = tangle.Execute();
}
