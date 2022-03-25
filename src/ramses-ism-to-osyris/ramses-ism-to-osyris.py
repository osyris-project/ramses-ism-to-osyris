# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Osyris contributors (https://github.com/osyris-project)

import argparse
import os
import shutil
import warnings

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--dir',
                    type=str,
                    default=None,
                    help='an integer for the accumulator')
parser.add_argument('--file',
                    type=str,
                    default=None,
                    help='sum the integers (default: find the max)')


def generate_fname(nout, path="", ftype="", cpuid=1, ext=""):

    if nout == -1:
        filelist = sorted(glob.glob(os.path.join(path, "output*")))
        number = filelist[-1].split("_")[-1]
    else:
        number = str(nout).zfill(5)

    infile = os.path.join(path, "output_" + number)
    if len(ftype) > 0:
        infile = os.path.join(infile, ftype + "_" + number)
        if cpuid > 0:
            infile += ".out" + str(cpuid).zfill(5)

    if len(ext) > 0:
        infile += ext

    return infile


def read_parameter_file(fname=None, delimiter="="):
    """
    Read info file and create dictionary
    """
    out = {}
    with open(fname, 'r') as f:
        content = f.readlines()
    for line in content:
        sp = line.split(delimiter)
        if len(sp) > 1:
            value = sp[1].strip()
            try:
                value = eval(value)
            except NameError:
                pass
            out[sp[0].strip()] = value
    return out


def write_file_descriptor(filename, variables):
    with open(filename, 'w') as f:
        f.write('# version:  1 \n# ivar, variable_name, variable_type\n')
        for i, var in enumerate(variables):
            f.write(f"{i}, {var['name']}, {var['type']}\n")


def convert_hydro(output):

    # Read the number of variables from the hydro_file_descriptor.txt
    # and select the ones to be read if specified by user
    hydro_file = os.path.join(output, "hydro_file_descriptor.txt")
    with open(hydro_file) as f:
        content = f.readlines()
    f.close()

    # Check that the file is indeed legacy format before changing it
    if "nvar" not in content[0]:
        raise RuntimeError(
            "The hydro_file_descriptor does not appear to be legacy format.")

    mapping = {
        "B_left_x": "B_x_left",
        "B_left_y": "B_y_left",
        "B_left_z": "B_z_left",
        "B_right_x": "B_x_right",
        "B_right_y": "B_y_right",
        "B_right_z": "B_z_right"
    }

    shutil.copyfile(hydro_file, f"{hydro_file}.backup")
    variables = []
    # counter = 0
    # with open(hydro_file, 'w') as f:
    #     f.write('# version:  1 \n# ivar, variable_name, variable_type\n')
    for line in content:
        sp = line.split(":")
        if len(sp) > 1:
            # counter += 1
            var = sp[1].strip()
            variables.append({"name": mapping.get(var, var), "type": "d"})
            # f.write(f"{counter}, {mapping.get(var, var)}, d\n")
    write_file_descriptor(filename=hydro_file, variables=variables)

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


def convert_part(output, ndim):

    part_file = os.path.join(output, "part_file_descriptor.txt")
    if os.path.exists(part_file):
        warnings.warn(f"{part_file} already exists, conversion skipped.")

    nout = output.split('_')[-1]
    print(nout)
    header_file = generate_fname(
        nout,
        # path,
        ftype="header",
        cpuid=-1,
        ext=".txt")
    print(header_file)

    try:
        with open(header_file, 'r') as f:
            content = f.readlines()
    except IOError:
        return

    particle_fields = content[-1].split()
    npart_fields = len(particle_fields)

    mapping = {
        "pos": {
            "ndim": ndim,
            "type": "d",
            "name": "position"
        },
        "vel": {
            "ndim": ndim,
            "type": "d",
            "name": "velocity"
        },
        "iord": {
            "ndim": 1,
            "type": "i",
            "name": "identity"
        },
        "level": {
            "ndim": 1,
            "type": "i",
            "name": "levelp"
        }
    }

    part_file = os.path.join(output, "part_file_descriptor.txt")
    variables = []
    # counter = 0
    # with open(part_file, 'w') as f:
    #     f.write('# version:  1 \n# ivar, variable_name, variable_type\n')
    for field in particle_fields:
        if field in mapping:
            for n in range(mapping[field]['ndim']):
                # counter += 1
                name = mapping[field]['name']
                if mapping[field]['ndim'] > 1:
                    name += '_' + 'xyz'[n]
                variables.append({"name": name, "type": mapping[field]["type"]})
                # f.write(f"{counter}, {name}, {mapping[field]['type']}\n")
        else:
            variables.append({"name": field, "type": "d"})
            # counter += 1
            # f.write(f"{counter}, {field}, d\n")
    write_file_descriptor(filename=part_file, variables=variables)


def convert_rt(output, ndim, write_cons):

    infofile = os.path.join(output, "info_rt_", output.split("_")[-1], ".txt")
    if not os.path.exists(infofile):
        return

    rt_file = os.path.join(output, "rt_file_descriptor.txt")
    if os.path.exists(rt_file):
        warnings.warn(f"{rt_file} already exists, conversion skipped.")

    # infor = self.read_parameter_file(fname=infortfile,
    #                                   dict_name="info_rt",
    #                                   verbose=True)
    info_rt = read_parameter_file(fname=infofile)

    variables = []

    # counter = 0
    # with open(rt_file, 'w') as f:
    for igrp in range(info_rt["nGroups"]):
        # counter += 1
        if write_cons == 1:
            name = "photon_density_"
        else:
            name = "photon_flux_density_"

        variables.append({"name": f"{name}{igrp+1}", "type": "d"})
        # f.write(f"{counter}, {name}{igrp+1}, d\n")

        for n in range(ndim):
            # counter += 1
            name = f"photon_flux_{igrp + 1}_{xyz_strings[n]}"
            variables.append({"name": f"{name}", "type": "d"})

    write_file_descriptor(filename=rt_file, variables=variables)

    # # Now add to the list of variables to be read
    # for line in content:
    #     if (len(variables) == 0) or (line.strip() in variables) or ("rt" in variables):
    #         var_read.append(True)
    #         list_vars.append(line.strip())
    #         var_group.append("rt")
    #     else:
    #         var_read.append(False)


def read_info(output):
    infofile = os.path.join(output, "info_" + output.split("_")[-1] + ".txt")
    return read_parameter_file(fname=infofile)


def convert(outputs):
    print(outputs)

    for output in outputs:
        info = read_info(output=output)
        convert_hydro(output=output)
        convert_part(output=output, ndim=info["ndim"])
        convert_rt(output=output,
                   ndim=info["ndim"],
                   write_cons=info.get("write_cons", None))

    return


if __name__ == "__main__":

    args = parser.parse_args()
    if args.file is not None:
        outputs = [args.file]
    elif args.dir is not None:
        print(os.listdir(args.dir))
        outputs = [
            os.path.join(args.dir, o) for o in os.listdir(args.dir) if "output_0" in o
        ]

    convert(outputs=outputs)
