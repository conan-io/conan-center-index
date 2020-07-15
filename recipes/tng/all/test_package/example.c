/* This code is part of the tng binary trajectory format.
 *
 * Written by Magnus Lundborg
 * Copyright (c) 2012-2013, The GROMACS development team.
 * check out http://www.gromacs.org for more information.
 *
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the Revised BSD License.
 */

#include "tng/tng_io.h"

#ifdef USE_STD_INTTYPES_H
#include <inttypes.h>
#endif

#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv)
{
    tng_trajectory_t traj;
    union data_values ***positions = 0; /* A 3-dimensional array to be populated */
    int64_t n_particles, n_values_per_frame, n_frames, tot_n_frames;
    char data_type;
    int i, j;
    int particle = 0;
    /* Set a default frame range */
    int first_frame = 0, last_frame = 50;
    char atom_name[64], res_name[64], chain_name[64];

    if(argc <= 1)
    {
        printf("No file specified\n");
        printf("Usage:\n");
        printf("tng_io_read_pos <tng_file> [particle number = %d] "
               "[first_frame = %d] [last_frame = %d]\n",
               particle, first_frame, last_frame);
        exit(1);
    }

    /* A reference must be passed to allocate memory */
    if(tng_trajectory_init(&traj) != TNG_SUCCESS)
    {
        tng_trajectory_destroy(&traj);
        exit(1);
    }
    tng_input_file_set(traj, argv[1]);

    /* Read the file headers */
    tng_file_headers_read(traj, TNG_USE_HASH);

    if(argc >= 3)
    {
        particle = strtol(argv[2], 0, 10);
        if(argc >= 4)
        {
            first_frame = strtol(argv[3], 0, 10);
            if(argc >= 5)
            {
                last_frame = strtol(argv[4], 0, 10);
            }
        }
    }

    if(tng_num_frames_get(traj, &tot_n_frames) != TNG_SUCCESS)
    {
        printf("Cannot determine the number of frames in the file\n");
        tng_trajectory_destroy(&traj);
        exit(1);
    }

    printf("%"PRId64" frames in file\n", tot_n_frames);

    if(last_frame > tot_n_frames - 1)
    {
        last_frame = tot_n_frames - 1;
    }

    n_frames = last_frame - first_frame + 1;

    if(tng_atom_name_of_particle_nr_get(traj, particle, atom_name,
                                        sizeof(atom_name)) ==
       TNG_SUCCESS &&
       tng_residue_name_of_particle_nr_get(traj, particle, res_name,
                                           sizeof(res_name)) ==
       TNG_SUCCESS &&
       tng_chain_name_of_particle_nr_get(traj, particle, chain_name,
                                         sizeof(chain_name)) ==
       TNG_SUCCESS)
    {
        printf("Particle: %s (%s: %s)\n", atom_name, chain_name, res_name);
    }
    else
    {
        printf("Particle name not found\n");
    }

    /* Get the positions of all particles in the requested frame range.
       The positions are stored in the positions array.
       N.B. No proper error checks. */
    if(tng_particle_data_interval_get(traj, TNG_TRAJ_POSITIONS, first_frame,
       last_frame, TNG_USE_HASH, &positions, &n_particles, &n_values_per_frame,
       &data_type) == TNG_SUCCESS)
    {
        if(particle >= n_particles)
        {
            printf("Chosen particle out of range. Only %"PRId64" particles in trajectory.\n", n_particles);
        }
        else
        {
            /* Print the positions of the wanted particle (zero based) */
            for(i=0; i<n_frames; i++)
            {
                printf("%d", first_frame + i);
                for(j=0; j<n_values_per_frame; j++)
                {
                    switch(data_type)
                    {
                    case TNG_INT_DATA:
                        printf("\t%"PRId64"", positions[i][particle][j].i);
                        break;
                    case TNG_FLOAT_DATA:
                        printf("\t%f", positions[i][particle][j].f);
                        break;
                    case TNG_DOUBLE_DATA:
                        printf("\t%f", positions[i][particle][j].d);
                        break;
                    default:
                        break;
                    }
                    printf("\n");
                }
            }
        }
    }
    else
    {
        printf("Cannot read positions\n");
    }

    /* Free memory */
    if(positions)
    {
        tng_particle_data_values_free(traj, positions, n_frames, n_particles,
                                      n_values_per_frame, data_type);
    }
    tng_trajectory_destroy(&traj);

    return(0);
}
