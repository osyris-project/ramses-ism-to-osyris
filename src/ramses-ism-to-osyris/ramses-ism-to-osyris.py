# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Osyris contributors (https://github.com/osyris-project)

import argparse
import os
import shutil

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--dir',
                    type=str,
                    default=None,
                    help='an integer for the accumulator')
parser.add_argument('--file',
                    type=str,
                    default=None,
                    help='sum the integers (default: find the max)')


def convert_hydro(output):

    # Read the number of variables from the hydro_file_descriptor.txt
    # and select the ones to be read if specified by user
    hydrofile = os.path.join(output, "hydro_file_descriptor.txt")
    with open(hydrofile) as f:
        content = f.readlines()
    f.close()

    mapping = {
        "B_left_x": "B_x_left",
        "B_left_y": "B_y_left",
        "B_left_z": "B_z_left",
        "B_right_x": "B_x_right",
        "B_right_y": "B_y_right",
        "B_right_z": "B_z_right"
    }

    shutil.copyfile(hydrofile, f"{hydrofile}.backup")
    counter = 0
    with open(hydrofile, 'w') as f:
        f.write('# version:  1 \n# ivar, variable_name, variable_type\n')
        for line in content:
            sp = line.split(":")
            if len(sp) > 1:
                counter += 1
                var = sp[1].strip()
                f.write(f"{counter}, {mapping.get(var, var)}, d\n")

    # # Now for gravity ==================================

    # # Check if self-gravity files exist
    # grav_fname = self.generate_fname(nout, path, ftype="grav", cpuid=1)
    # try:
    #     with open(grav_fname,
    #               mode='rb') as grav_file:  # b is important -> binary
    #         gravContent = grav_file.read()
    #     grav_file.close()
    #     gravity = True
    # except IOError:
    #     gravity = False

    # # Add gravity fields
    # if gravity:
    #     content = ["grav_potential"]
    #     for n in range(self.info["ndim"]):
    #         content.append("grav_acceleration_" + xyz_strings[n])

    #     # Now add to the list of variables to be read
    #     for line in content:
    #         if (len(variables) == 0) or (line.strip() in variables) or (
    #                 "gravity" in variables) or ("grav" in variables):
    #             var_read.append(True)
    #             list_vars.append(line.strip())
    #             var_group.append("grav")
    #         else:
    #             var_read.append(False)

    # # Now for rt ==================================

    # # Check if rt files exist
    # rt_fname = self.generate_fname(nout, path, ftype="rt", cpuid=1)
    # try:
    #     with open(rt_fname, mode='rb') as rt_file:  # b is important -> binary
    #         rtContent = rt_file.read()
    #     rt_file.close()
    #     rt = True
    # except IOError:
    #     rt = False

    # # Read info_rt file and create info_rt dictionary
    # if rt:
    #     infortfile = infile + "/info_rt_" + infile.split("_")[-1] + ".txt"
    #     status = self.read_parameter_file(fname=infortfile,
    #                                       dict_name="info_rt",
    #                                       verbose=True)
    #     if status < 1:
    #         return 0

    # # Add rt fields
    # if rt:
    #     content = []
    #     for igrp in range(self.info_rt["nGroups"]):
    #         if self.info["write_cons"] == 1:
    #             content.append("photon_density_" + str(igrp + 1))
    #         else:
    #             content.append("photon_flux_density_" + str(igrp + 1))
    #         for n in range(self.info["ndim"]):
    #             content.append("photon_flux_" + str(igrp + 1) + "_" +
    #                            xyz_strings[n])

    #     # Now add to the list of variables to be read
    #     for line in content:
    #         if (len(variables) == 0) or (line.strip()
    #                                      in variables) or ("rt" in variables):
    #             var_read.append(True)
    #             list_vars.append(line.strip())
    #             var_group.append("rt")
    #         else:
    #             var_read.append(False)

    # # Make sure we always read the coordinates
    # list_vars.extend(("level", "x", "y", "z", "dx", "cpu", "leaf"))
    # var_read.extend((True, True, True, True, True, True, True))
    # var_group.extend(("amr", "amr", "amr", "amr", "amr", "amr", "amr"))
    # nvar_read = len(list_vars)

    # # Now for particles ==================================

    # particles = False
    # self.info["npart_tot"] = 0
    # if "part" in variables:
    #     # Read header file to get particle information
    #     headerfile = self.generate_fname(nout,
    #                                      path,
    #                                      ftype="header",
    #                                      cpuid=-1,
    #                                      ext=".txt")
    #     with open(headerfile) as f:
    #         dummy_string = f.readline()
    #         self.info["npart_tot"] = int(f.readline())
    #         dummy_string = f.readline()
    #         self.info["npart_dm"] = int(f.readline())
    #         dummy_string = f.readline()
    #         self.info["npart_star"] = int(f.readline())
    #         dummy_string = f.readline()
    #         self.info["npart_sink"] = int(f.readline())
    #         dummy_string = f.readline()
    #         particle_fields = f.readline().split(' ')[:-1]
    #     f.close()
    #     npart_fields = len(particle_fields)
    #     particles = (self.info["npart_tot"] > 0)
    #     npart_count = 0
    #     if particles:
    #         npart_dims = []
    #         part_vars = []
    #         part_types = []
    #         for field in particle_fields:
    #             if field == "pos":
    #                 for n in range(self.info["ndim"]):
    #                     part_vars.append(xyz_strings[n] + "_part")
    #                     part_types.append("d")
    #                 npart_dims.append(self.info["ndim"])
    #             elif field == "vel":
    #                 for n in range(self.info["ndim"]):
    #                     part_vars.append("part_velocity_" + xyz_strings[n])
    #                     part_types.append("d")
    #                 npart_dims.append(self.info["ndim"])
    #             elif field == "tracer_b":
    #                 for n in range(3):
    #                     part_vars.append("part_" + field + "_" +
    #                                      xyz_strings[n])
    #                     part_types.append("d")
    #                 npart_dims.append(3)
    #             else:
    #                 part_vars.append("part_" + field)
    #                 npart_dims.append(1)
    #                 if field == "iord":
    #                     part_types.append("q")
    #                 elif field == "level":
    #                     part_types.append("i")
    #                 else:
    #                     part_types.append("d")
    #         #print sum(npart_dims)
    #         part = np.zeros([self.info["npart_tot"],
    #                          sum(npart_dims)],
    #                         dtype=np.float64)


def convert(outputs):
    print(outputs)

    for output in outputs:
        convert_hydro(output=output)

    return


if __name__ == "__main__":

    args = parser.parse_args()

    if args.file is not None:
        outputs = [args.file]
    elif args.dir is not None:
        print(os.listdir(args.dir))
        outputs = [
            os.path.join(args.dir, o) for o in os.listdir(args.dir)
            if "output_0" in o
        ]

    convert(outputs=outputs)

# for infile in infiles:
#    infile+='/'
#    fname=infile+"hydro_file_descriptor.txt"
#    print(fname)
#    HydroConverter.hydroFileDescriptor(infile,fname)

#     convert()
