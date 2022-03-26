# ramses-ism-to-osyris

Convert old `ramses_ism` outputs file format to work with `osyris` 2.0.

## Usage

### Convert all outputs in a folder

`python ramses-ism-to-osyris.py --dir=.`

### Convert a single output

`python ramses-ism-to-osyris.py --output=output_00001`

### Specify custom hydro variables

`python ramses-ism-to-osyris.py --output=output_00001 --hydro density velocity_x velocity_y pressure`

Use `--part` or `--rt` to specify particle and rt variables.

### Specify custom hydro variables with type

`python ramses-ism-to-osyris.py --output=output_00001 --hydro density,d velocity_x level,i`

Type key:
- `d`: double precision
- `i`: integer
- `b`: boolean
