#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <dc1394/dc1394.h>

int main()
{
	dc1394_t *dc1394 = NULL;
	dc1394error_t error;
	dc1394camera_list_t *cameras = NULL;

	dc1394 = dc1394_new();
	if (!dc1394)
	{
		fprintf(stderr, "cannot create dc1394!\n");
		fprintf(stderr, "This is a test package, so ignore!\n");
		return EXIT_SUCCESS;
	}
	error = dc1394_camera_enumerate(dc1394, &cameras);
	if ((error > 0) || (error <= -DC1394_ERROR_NUM))
	{
		fprintf(stderr, "failed to enumerate cameras!\n");
		dc1394_free(dc1394);
		fprintf(stderr, "This is a test package, so ignore! (better luck next time)\n");
		return EXIT_SUCCESS;
	}
	if (cameras->num == 0)
	{
		fprintf(stderr, "no cameras were found!\n");
	}
	else
	{
		int i = 0;
		for (i = 0; i < cameras->num; ++i)
		{
			dc1394camera_t *camera = NULL;
			camera = dc1394_camera_new(dc1394, cameras->ids[i].guid);
			if (!camera)
			{
				fprintf(stderr, "failed to initialize camera %d\n", i);
			}
			else
			{
				printf("camera %s vendor %s\n", camera->model, camera->vendor);
				dc1394_camera_free(camera);
			}
		}
	}
	dc1394_camera_free_list(cameras);
	dc1394_free(dc1394);
	return EXIT_SUCCESS;
}
