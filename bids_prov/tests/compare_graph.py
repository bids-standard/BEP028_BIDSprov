import json
import os.path
import rdflib
import requests
import pyld
import rdflib.compare


def load_jsonld11_for_rdf(jsonld11_file: str, pyld_convert=True) -> dict:
    """ Load json file and convert them to json-ld1.1 version

    Parameters
    ----------
    jsonld11_file : file_path of json-ld
    pyld_convert : boolean to convert or not to 1.1 json-ld

    """
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


def is_similar_rdf_graph(g1: rdflib.Graph, g2: rdflib.Graph, verbose=False) -> bool:
    """ A wrapping function that compare rdf graph, and if they are not similar show differences

    Parameters
    ----------
    g1 : first rdf graph
    g2 : second rdf graph
    verbose : boolean to have more verbosity

    """
    cmp = rdflib.compare.similar(g1, g2) # Checks if the two graphs are “similar”.
    # Checks if the two graphs are “similar”, by comparing sorted triples where all bnodes have been replaced by a
    # singular mock bnode (the _MOCK_BNODE).

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
    """ A wrapping function that print differences between 2 graph

    Parameters
    ----------
    g1 : first rdf graph
    g2 : second rdf graph

    """
    in_both, in_g1, in_g2 = rdflib.compare.graph_diff(g1, g2)

    for graph, text in zip([in_both, in_g1, in_g2],
                           ["common part", "only in_g1", "only in_g2"]):
        print('=' * 10, text, ' begin')
        print(graph_to_str(graph))
        print('=' * 10, text, ' end')


def is_included_rdf_graph(g1: rdflib.Graph, g2: rdflib.Graph, verbose=False) -> bool:
    """ A wrapping function that print differences between 2 graph

    Parameters
    ----------
    g1 : first rdf graph
    g2 : second rdf graph
    verbose : boolean to have more verbosity

    """
    in_both, in_g1, in_g2 = rdflib.compare.graph_diff(g1, g2) # in_g1 is a list of elements only in g1

    if verbose:
        for graph, text in zip([in_both, in_g1, in_g2],
                               ["common part", "only in_g1", "only in_g2"]):
            print('=' * 10, text, ' begin')
            print(graph_to_str(graph))
            print('=' * 10, text, ' end')

    return len(in_g1)==0



def graph_to_str(graph: rdflib.Graph) -> str:
    """ A tool function to print enumerate triplet in rdf graph under turtle format

    """
    lines = graph.serialize(format='turtle').splitlines()
    res = ''
    for line in lines:
        if line:  # not empty line ''
            res = res + '\n' + line
    return res


if __name__ == '__main__':

    ref_jsonld = os.path.abspath("./to_test/batch_example_spm_seed14.jsonld")
    new_jsonld = os.path.abspath("./to_test/batch_example_spm_seed14.jsonld")

    jsonld11_ref = load_jsonld11_for_rdf(ref_jsonld, pyld_convert=True)
    graph_ref = rdflib.ConjunctiveGraph()  # https://rdflib.readthedocs.io/en/stable/_modules/rdflib/graph.html#ConjunctiveGraph
    graph_ref.parse(data=json.dumps(jsonld11_ref, indent=2), format='json-ld')

    jsonld11_new = load_jsonld11_for_rdf(new_jsonld, pyld_convert=True)
    graph_new = rdflib.ConjunctiveGraph()  # https://rdflib.readthedocs.io/en/stable/_modules/rdflib/graph.html#ConjunctiveGraph
    graph_new.parse(data=json.dumps(jsonld11_new, indent=2), format='json-ld')

    # print(graph_to_str(graph_new))
    # print("___"*30)
    # print(graph_to_str(graph_ref))
    res = is_included_rdf_graph(graph_new, graph_ref, verbose=False)
    # # iso1 = rdflib.compare.to_isomorphic(g)
    # # iso2 = rdflib.compare.to_isomorphic(g2)
    # cmp = compare_rdf_graph(graph_new, graph_ref, verbose=True)
