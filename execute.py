# -*- coding: utf-8 -*-
# !/usr/bin/env python

# %%
from shaclgen.shaclgen import data_graph
from shaclgen.schema import schema

import argparse
from argparse import RawDescriptionHelpFormatter
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser(
    formatter_class=RawDescriptionHelpFormatter,
    description=("""
    ---------------------------Shaclgen------------------------------------------

    Shaclgen takes either a data graph(s) or schema(s) as input and generates 
    a basic shape file based on the classes and properties present. 

    usage:
        shaclgen [path to graph] [optional arguments]
        $ shaclgen https://www.lib.washington.edu/static/public/cams/data/datasets/uwSemWebParts/webResource-1-0-0.nt -ns www.example.org exam

    Multiple graphs:
    To load multiple graphs simply list all the graphs one after the other. RDF serializtion does not matter.
    example:
        $ shaclgen https://www.lib.washington.edu/static/public/cams/data/datasets/uwSemWebParts/webResource-1-0-0.nt https://www.lib.washington.edu/static/public/cams/data/datasets/uwSemWebParts/collection-1-0-0.ttl

    Shape files from data graphs:
    By default, the input graph is processed as instance triples.

    Shape files from ontologies:
    If the input is a schema or ontology (-o), shaclgen will generate 
    a nested shape file: properties with rdfs:domain defined in the ontology 
    will be nested within the appropriate NodeShape. rdfs:range definitions
    for XML and rdfs datatypes are included.

    Serialization options:
        turtle = turtle
        ntriples = nt
        rdfxml = xml
        n3 = n3

    """))

parser.add_argument("graph", nargs='+', type=str, help="The data graph(s).")

group = parser.add_mutually_exclusive_group()
group.add_argument("-nf", "--nested", action="store_true", help='generates a nested shape file')
group.add_argument("-ef", "--extended", action="store_true", help='generates an expanded shape file')
parser.add_argument("-o", "--ontology", action="store_true", help='input file(s) or URL(s) is a schema or ontology')
parser.add_argument("-s", "--serialization", help='result graph serialization, default is turtle. example: -s nt')
parser.add_argument("-ns", "--namespace", nargs='+',
                    help="optional shape namespace declaration. example: -ns http://www.example.com exam")

args = parser.parse_args()


def main():
    if args.ontology:
        print("IF  args.ontology: ")
        g = schema(args.graph)
        kwargs = {'serial': 'turtle'}
        if args.serialization:
            kwargs['serial'] = args.serialization
        if args.namespace:
            kwargs['namespace'] = args.namespace
        g.gen_graph(**kwargs)
    else:
        print("Else rdf graph....")
        kwargs = {'serial': 'turtle'}
        print("Starting to load graph ....")
        g = data_graph(args.graph)
        print("Graph is parsed....  g = data_graph(args.graph)")
        #        if args.nested:
        #            kwargs['graph_format'] = 'nf'
        #        elif args.extended:
        #            kwargs['graph_format'] = 'ef'
        if args.serialization:
            kwargs['serial'] = args.serialization
        if args.namespace:
            kwargs['namespace'] = args.namespace
        print('## shape file generated by SHACLGEN')
        g.gen_graph(**kwargs)


if __name__ == '__main__':
    main()

