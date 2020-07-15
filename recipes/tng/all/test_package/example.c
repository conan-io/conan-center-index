#include <stdlib.h>
#include <stdio.h>
#include "tng/tng_io.h"

 int test_file(char * path)
 {
     tng_trajectory_t traj;
     // Assume that the data is stored as floats. The data is placed in 1-D
     // arrays
     float *positions = 0, *box_shape = 0;
     int64_t n_particles, n_frames, tot_n_frames, stride_length, i, j;
     // Set a default frame range
     int64_t first_frame = 0, last_frame = 5000;
     int k;

     // A reference must be passed to allocate memory
     tng_util_trajectory_open(path, 'r', &traj);

     if(tng_num_frames_get(traj, &tot_n_frames) != TNG_SUCCESS)
     {
         printf("Cannot determine the number of frames in the file\n");
         tng_util_trajectory_close(&traj);
         exit(0);
     }

     if(tng_num_particles_get(traj, &n_particles) != TNG_SUCCESS)
     {
         printf("Cannot determine the number of particles in the file\n");
         tng_util_trajectory_close(&traj);
         exit(1);
     }

     printf("%ld frames in file\n", tot_n_frames);

     if(last_frame > tot_n_frames - 1)
     {
         last_frame = tot_n_frames - 1;
     }

     if(tng_util_box_shape_read(traj, &box_shape, &stride_length) ==
         TNG_SUCCESS)
     {
         printf("Simulation box shape: ");
         for(i=0; i < 9; i++)
         {
             printf("%f ", box_shape[i]);
         }
         printf("\n");
     }
     else
     {
         printf("Simulation box shape not set in the file (or could not be read)\n");
     }

     n_frames = last_frame - first_frame + 1;


     // Get the positions of all particles in the requested frame range.
     // The positions are stored in the positions array.
     // N.B. No proper error checks.
     if(tng_util_pos_read_range(traj, 0, last_frame, &positions, &stride_length)
        == TNG_SUCCESS)
     {
         // Print the positions of the wanted particle (zero based)
         for(i=0; i < n_frames; i += stride_length)
         {
             printf("\nFrame %ld:\n", first_frame + i);
             for(j=0; j < n_particles; j++)
             {
                 printf("Atom nr: %ld", j);
                 for(k=0; k < 3; k++)
                 {
                     printf("\t%f", positions[i/stride_length*n_particles*
                                              3+j*3+k]);
                 }
                 printf("\n");
             }
         }
     }
     else
     {
         printf("Cannot read positions\n");
     }

     // Free memory
     if(positions)
     {
         free(positions);
     }
     tng_util_trajectory_close(&traj);

     return(0);
 }

int main(int argc, char **argv)
{
	if( argc == 25)
	{
		return test_file(argv[1]);
	}
	return 0;
}
