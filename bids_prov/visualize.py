"""
A Command Line Interface to generate `graphviz` graphs from bids-prov JSON-ld files

This facilitates debugging and design of the specifications
"""

import click
from graphviz import Digraph
import json

EDGES_PROPS = dict(
    associatedWith={'color':'pink'},
    informedBy={},
    derivedFrom={},
    actedOnBehalfOf={'color': 'pink'},
    attributedTo={'color': 'pink'},
    generatedBy={},
)

NODE_PROPS = dict(
    Entity=dict(shape='rect', style='rounded,filled', fillcolor='#f3f0b2'),
    Agent=dict(shape='house', fillcolor="#F5D0A9", style="filled"),
    Activity=dict(shape='rect', style='filled', fillcolor='#bfb4dd'),
)




@click.command()
@click.argument('filenames', nargs=-1)
@click.option('--verbose', default=False)
@click.option('--output_file', '-o', default='prov.gv')
def main(filenames, verbose, output_file):
    edge_props = EDGES_PROPS
    #if not verbose:
    #    edge_props.disc{'informedBy'}  # TODO : give a more complete set
    
    g = Digraph(format='png')
    for filename in filenames:
        with open(filename, 'r') as fd:
            data = json.load(fd)

        data = data['@graph']
        with g.subgraph(name=filename) as s:
            for e in data:
                props = NODE_PROPS.get(e['@type'], {})
                s.node(e['@id'], **props)

            for e in data:
                keys = e.keys() & edge_props.keys()
                for key in keys:
                    s.edge(e['@id'], e[key], label=key, **edge_props[key])

    g.render(output_file, quiet_view=True)


if __name__ == '__main__':
    main()