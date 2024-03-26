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

// for testing autoinit
#include <vtkTextRenderer.h>

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

  vtkSmartPointer<vtkTextRenderer> textrender = vtkSmartPointer<vtkTextRenderer>::New();

  if (textrender)
  {
     std::cout << "Check AutoInit TextRenderer:" << std::endl;
     textrender->PrintSelf(std::cout, vtkIndent(3));
     std::cout << std::endl;
  }
  else
  {
     std::cout << "ERROR: Did NOT create TextRenderer ... autoinit not working?" << std::endl;
  }

  return EXIT_SUCCESS;
}
