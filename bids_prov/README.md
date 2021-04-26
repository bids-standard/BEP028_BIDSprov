## CLI scripts for BIDS PROV

### Notes
All scripts provide a `--help` flag, to get an overview of possible parameters and default values
Here is an example
```bash
>> python bids_prov/visualize.py --help
Usage: visualize.py [OPTIONS] [FILENAMES]...

Options:
  -o, --output_file TEXT
  --omit-details          omit the following low level details : {'Activity':
                          ('startedAtTime', 'endedAtTime'), 'Entity':
                          ('atLocation', 'generatedAt')}

  --help                  Show this message and exit.
```