#include <iostream>

/* ONLY available if 'rendering' was enabled...
 * TODO detect if rendering was enabled, and test this?
 *
#include <vtkConeSource.h>
#include <vtkPolyData.h>
#include <vtkSmartPointer.h>
#include <vtkPolyDataMapper.h>
#include <vtkActor.h>
#include <vtkRenderWindow.h>
#include <vtkRenderer.h>
#include <vtkRenderWindowInteractor.h>
*/

#include <vtkVersion.h>
#include <vtkIntArray.h>

int main(int, char *[])
{
  //Create a cone
   /* ONLY if 'rendering' is enabled
  vtkSmartPointer<vtkConeSource> coneSource =
    vtkSmartPointer<vtkConeSource>::New();
  coneSource->Update();
  auto cone = coneSource->GetOutput();
  std::cout << "Cone has " <<cone->GetNumberOfPoints() << " of 7 points." << std::endl;
  */

  vtkSmartPointer<vtkIntArray> numbers = vtkSmartPointer<vtkIntArray>::New();

  std::cout << "Using VTK version " << GetVTKVersion() << std::endl;

  return EXIT_SUCCESS;
}
