#include "vtkPolyData.h"
#include "vtkImageData.h"
#include "vtkFillHolesFilter.h"
#include "vtkNew.h"

int main() {
    vtkNew<vtkPolyData> PolyInst;
    vtkNew<vtkImageData> ImgInst;
    vtkNew<vtkFillHolesFilter> FilterInst;
}
