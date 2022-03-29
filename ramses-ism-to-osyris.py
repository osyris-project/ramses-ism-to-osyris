# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Osyris contributors (https://github.com/osyris-project)

import argparse
import os
import shutil
import warnings

parser = argparse.ArgumentParser(description='Convert legacy Ramses output formats to '
                                 'new format that can be read by Osyris.')
parser.add_argument('--dir',
                    type=str,
                    default=None,
                    help='the directory which contains the outputs')
parser.add_argument('--output',
                    type=str,
                    default=None,
                    help='a single output folder that will be converted')
parser.add_argument(
    '--hydro',
    nargs='+',
    type=str,
    required=False,
    help='a list of hydro variables to override the ones found in the output')
parser.add_argument(
    '--part',
    nargs='+',
    type=str,
    required=False,
    help='a list of part variables to override the ones found in the output')
parser.add_argument(
    '--rt',
    nargs='+',
    type=str,
    required=False,
    help='a list of rt variables to override the ones found in the output')


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
            f.write(f"{i+1}, {var['name']}, {var['type']}\n")


def override_variables(variables):
    out = []
    for var in variables:
        if "," in var:
            var_name, var_type = var.split(',')
        else:
            var_name = var
            var_type = "d"
        out.append({"name": var_name, "type": var_type})
    return out


def convert_hydro(output, hydro_variables):

    hydro_file = os.path.join(output, "hydro_file_descriptor.txt")
    try:
        with open(hydro_file) as f:
            content = f.readlines()
    except IOError:
        return

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

    if hydro_variables is None:
        variables = []
        for line in content:
            sp = line.split(":")
            if len(sp) > 1:
                var = sp[1].strip()
                variables.append({"name": mapping.get(var, var), "type": "d"})
    else:
        variables = override_variables(hydro_variables)

    write_file_descriptor(filename=hydro_file, variables=variables)


def convert_part(output, part_variables, ndim):

    part_file = os.path.join(output, "part_file_descriptor.txt")
    if os.path.exists(part_file):
        warnings.warn(f"{part_file} already exists, conversion skipped.")
        return

    nout = output.split('_')[-1]
    header_file = os.path.join(output, f"header_{nout}.txt")
    try:
        with open(header_file, 'r') as f:
            content = f.readlines()
    except IOError:
        return

    particle_fields = content[-1].split()

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
    if part_variables is None:
        variables = []
        for field in particle_fields:
            if field in mapping:
                for n in range(mapping[field]['ndim']):
                    name = mapping[field]['name']
                    if mapping[field]['ndim'] > 1:
                        name += '_' + 'xyz'[n]
                    variables.append({"name": name, "type": mapping[field]["type"]})
            else:
                variables.append({"name": field, "type": "d"})
    else:
        variables = override_variables(part_variables)

    write_file_descriptor(filename=part_file, variables=variables)


def convert_rt(output, rt_variables, ndim, write_cons):
    infofile = os.path.join(output, "info_rt_", output.split("_")[-1], ".txt")
    if not os.path.exists(infofile):
        return

    rt_file = os.path.join(output, "rt_file_descriptor.txt")
    if os.path.exists(rt_file):
        warnings.warn(f"{rt_file} already exists, conversion skipped.")
        return

    info_rt = read_parameter_file(fname=infofile)
    if rt_variables is None:
        variables = []
        for igrp in range(info_rt["nGroups"]):
            if write_cons == 1:
                name = "photon_density_"
            else:
                name = "photon_flux_density_"
            variables.append({"name": f"{name}{igrp+1}", "type": "d"})
            for n in range(ndim):
                name = f"photon_flux_{igrp + 1}_{'xyz'[n]}"
                variables.append({"name": f"{name}", "type": "d"})
    else:
        variables = override_variables(rt_variables)

    write_file_descriptor(filename=rt_file, variables=variables)


def convert_sinks(output):
    infofile = os.path.join(output, "sink_" + output.split("_")[-1] + ".info")
    if not os.path.exists(infofile):
        return

    csvfile = os.path.join(output, "sink_" + output.split("_")[-1] + ".csv")
    with open(csvfile, 'r') as f:
        csvdata = f.readlines()
    if csvdata[0].strip().startswith("#"):
        raise RuntimeError("The sink.csv file does not appear to be legacy format.")

    with open(infofile, 'r') as f:
        info_sink = f.readlines()
    for line in info_sink:
        if line.strip().startswith("Id"):
            info_line = line
            break

    unit_mapping = {
        "[Lsol]": "[L_sol]",
        "[Msol]": "[M_sol]",
        "[y]": "[year]",
        "[Msol/y]": "[M_sol/year]"
    }

    code_unit_quantities = {
        "x": "l",
        "y": "l",
        "z": "l",
        "vx": "l t**-1",
        "vy": "l t**-1",
        "vz": "l t**-1"
    }

    names_and_units = info_line.split()
    names = []
    units = []
    for var in names_and_units:
        name = var.split("[")[0]
        names.append(name)
        if all(x in var for x in ["[", "]"]):
            unit = "[" + var.split("[")[1].split("]")[0].strip() + "]"
        else:
            unit = code_unit_quantities.get(name, "1")
        units.append(unit_mapping.get(unit, unit))

    shutil.copyfile(csvfile, f"{csvfile}.backup")
    with open(csvfile, 'w') as f:
        f.write("# " + ",".join(names) + "\n")
        f.write("# " + ",".join(units) + "\n")
        for line in csvdata:
            f.write(line)


def read_info(output):
    infofile = os.path.join(output, "info_" + output.split("_")[-1] + ".txt")
    return read_parameter_file(fname=infofile)


def convert(outputs, hydro_variables=None, part_variables=None, rt_variables=None):
    for output in outputs:
        print(f"Processing {output}")
        info = read_info(output=output)
        convert_hydro(output=output, hydro_variables=hydro_variables)
        convert_part(output=output, part_variables=part_variables, ndim=info["ndim"])
        convert_rt(output=output,
                   rt_variables=rt_variables,
                   ndim=info["ndim"],
                   write_cons=info.get("write_cons", None))
        convert_sinks(output=output)


if __name__ == "__main__":

    args = parser.parse_args()
    if args.output is not None:
        outputs = [args.output]
    elif args.dir is not None:
        outputs = [
            os.path.join(args.dir, o) for o in os.listdir(args.dir) if "output_" in o
        ]

    convert(outputs=outputs,
            hydro_variables=args.hydro,
            part_variables=args.part,
            rt_variables=args.rt)
