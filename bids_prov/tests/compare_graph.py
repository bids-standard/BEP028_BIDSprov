import json
import os.path

import rdflib
import requests
import pyld
import rdflib.compare


def load_jsonld11_for_rdf(jsonld11_file: str, pyld_convert=True):
    with open(jsonld11_file) as fd:
        jsonld11 = json.load(fd)

    req_context_11 = requests.get(url=jsonld11['@context'])
    context_11 = req_context_11.json()
    context_10 = {k: v for k, v in context_11['@context'].items() if k not in {'@version', 'records'}}

    if pyld_convert:
        pyld_jsonld11 = pyld.jsonld.compact(jsonld11, context_10)
        jsonld11 = pyld_jsonld11
    else:
        jsonld11['@context'] = context_10

    return jsonld11


def compare_rdf_graph(g1: rdflib.Graph, g2: rdflib.Graph, verbose=False) -> bool:
    cmp = rdflib.compare.similar(g1, g2)

    if cmp:
        if verbose:
            print("inputs rdf graph are similar")
        # if rdflib.compare.isomorphic(g1, g2): # more restrictive
        #     if verbose:
        #         print("they are also isomorphic")
    else:
        if verbose:
            print("inputs rdf graph are not similar")
            show_diff(g1, g2)
    return cmp


def show_diff(g1: rdflib.Graph, g2: rdflib.Graph) -> None:
    in_both, in_g1, in_g2 = rdflib.compare.graph_diff(g1, g2)

    for graph, text in zip([in_both, in_g1, in_g2],
                           ["common part", "only in_g1", "only in_g2"]):
        print('=' * 10, text, ' begin')
        print(graph_to_str(graph))
        print('=' * 10, text, ' end')


def graph_to_str(graph: rdflib.Graph) -> str:
    lines = graph.serialize(format='turtle').splitlines()
    res = ''
    for line in lines:
        if line:  # not ''
            res = res + '\n' + line
    return res


if __name__ == '__main__':
    filenames = ['./samples_test/batch_example_spm_ref.jsonld',
                 '../nidm-examples/spm_covariate/batch_ref.jsonld'
                 ]
    new_jsonld = os.path.abspath("./samples_test/batch_example_spm.jsonld")
    ref_jsonld = os.path.abspath("./samples_test/batch_example_spm_ref.jsonld")

    print(ref_jsonld)
    jsonld11_ref = load_jsonld11_for_rdf(ref_jsonld, pyld_convert=True)
    graph_ref = rdflib.ConjunctiveGraph()  # https://rdflib.readthedocs.io/en/stable/_modules/rdflib/graph.html#ConjunctiveGraph
    graph_ref.parse(data=json.dumps(jsonld11_ref, indent=2), format='json-ld')

    jsonld11_new = load_jsonld11_for_rdf(new_jsonld, pyld_convert=True)
    graph_new = rdflib.ConjunctiveGraph()  # https://rdflib.readthedocs.io/en/stable/_modules/rdflib/graph.html#ConjunctiveGraph
    graph_new.parse(data=json.dumps(jsonld11_new, indent=2), format='json-ld')

    # g = rdflib.ConjunctiveGraph()  # https://rdflib.readthedocs.io/en/stable/_modules/rdflib/graph.html#ConjunctiveGraph
    # g.parse(data=json.dumps(jsonld11, indent=2), format='json-ld')
    #
    # g2 = rdflib.ConjunctiveGraph()  # https://rdflib.readthedocs.io/en/stable/_modules/rdflib/graph.html#ConjunctiveGraph
    # g2.parse(data=json.dumps(jsonld11, indent=2, sort_keys=True), format='json-ld')

    # iso1 = rdflib.compare.to_isomorphic(g)
    # iso2 = rdflib.compare.to_isomorphic(g2)
    cmp = compare_rdf_graph(graph_new, graph_ref, verbose=True)
    # graph_Lee = Graph()
    # graph_Lee.parse("http://www.w3.org/People/Berners-Lee/card")
    # print_g(graph_Lee)
