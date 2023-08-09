from loguru import logger
from rdflib import Namespace, Literal, Graph
import rdflib
from rdflib import URIRef
import collections
from rdflib.namespace import RDF, RDFS, SH
from rdflib.namespace import NamespaceManager
from rdflib.namespace import split_uri
from uuid import NAMESPACE_URL, uuid5
from .generator import Generator

SHGEN = Namespace("http://shaclgen/")


class data_graph(Generator):
    def __init__(self, graph: Graph, namespaces=None):
        self.G = graph
        if namespaces:
            self.namespaces = namespaces
        else:
            self.namespaces = NamespaceManager(graph=Graph())
        self.namespaces.bind("sh", SH)
        self.namespaces.bind("shgen", SHGEN)
        self.shapes_graph_iri = SHGEN

    def gen_graph(self, namespace=None, implicit_class_target=False):
        logger.info("Start Extraction of the Data Graph")
        ng = rdflib.Graph(namespace_manager=self.namespaces)

        ng = self.generate_inversePropertyShapes(ng)
        ng = self.generate_PropertyShapes(ng)
        ng = self.generate_NodeShapes(ng)

        return ng

    def generate_inversePropertyShapes(self, shape_graph):

        generate_inversePropertyShapes_query = """
prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
prefix sh:    <http://www.w3.org/ns/shacl#>
prefix shui:  <https://vocab.eccenca.com/shui/>
prefix owl:   <http://www.w3.org/2002/07/owl#>
prefix xsd:   <http://www.w3.org/2001/XMLSchema#>
prefix icontact: <https://vocab.eccenca.com/icontact/>
prefix gist: <https://ontologies.semanticarts.com/gist/>
prefix vd: <https://ns.eccenca.com/data/viridium-demo/>
prefix vv: <https://ns.eccenca.com/vocab/viridium-demo/>

CONSTRUCT {
  ?nodeShape sh:property ?propShape .
  ?propShape a sh:PropertyShape ;
    rdfs:label ?label ;
    sh:name ?name ;
    sh:path ?prop ;
    sh:description ?propDesc ;
    shui:inversePath true ;
    sh:nodeKind ?nodeKind .
}
WHERE {
  ?res a ?class .
  BIND(IRI(CONCAT(STR(?class), "-NodeShape")) AS ?nodeShape)

  ?s ?prop ?res .
  BIND(sh:IRI AS ?nodeKind)
  OPTIONAL { ?prop rdfs:label ?propL . }
  BIND(REPLACE(STR(?prop), ".*[/#]([^/#])", "$1") AS ?propLocal)
  BIND(IF(BOUND(?propL), STR(?propL), ?propLocal) AS ?label)
  BIND(STRLANG(CONCAT("⬅ ", STR(?label)), "en") AS ?name)
  OPTIONAL { ?prop rdfs:comment ?propD . }
  BIND(
    IF(BOUND(?propD),
      STRLANG(CONCAT("(inverse), ", STR(?propD)), "en"),
      STRLANG("(inverse), TODO: Comment and/or property declaration missing!", "en"))
    AS ?propDesc)
  BIND(URI(CONCAT(STR(?prop), "-InversePropertyShape")) AS ?propShape ) .
}
        """
        shape_graph += self.G.query(generate_inversePropertyShapes_query)

        return shape_graph

    def generate_PropertyShapes(self, shape_graph):

        generate_PropertyShapes_query = """
prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
prefix sh:    <http://www.w3.org/ns/shacl#>
prefix shui:  <https://vocab.eccenca.com/shui/>
prefix owl:   <http://www.w3.org/2002/07/owl#>
prefix xsd:   <http://www.w3.org/2001/XMLSchema#>

CONSTRUCT {
  ?nodeShape sh:property ?propShape .
  ?propShape a sh:PropertyShape ;
    rdfs:label ?label ;
    sh:name ?name ;
    sh:path ?prop ;
    sh:description ?propDesc .
  ?propShape sh:nodeKind ?nodeKind .
  ?propShape sh:datatype ?datatype .
}
WHERE {
  ?res a ?class .
  BIND(IRI(CONCAT(STR(?class), "-NodeShape")) AS ?nodeShape)

  ?res ?prop ?o .
  BIND(IF(isIRI(?o), sh:IRI, sh:Literal) AS ?nodeKind)
  BIND(DATATYPE(?o) AS ?datatype)
  OPTIONAL { ?prop rdfs:label ?propL . }
  BIND(REPLACE(STR(?prop), ".*[/#]([^/#])", "$1") AS ?propLocal)
  BIND(IF(BOUND(?propL), STR(?propL), ?propLocal) AS ?label)
  BIND(STRLANG(STR(?label), "en") AS ?name)
  OPTIONAL { ?prop rdfs:comment ?propD . }
  BIND(IF(BOUND(?propD), STRLANG(STR(?propD), "en"), STRLANG("TODO: Comment and/or property declaration missing!", "en")) AS ?propDesc)
  BIND(URI(CONCAT(STR(?prop), "-PropertyShape")) AS ?propShape ) .
}
        """
        shape_graph += self.G.query(generate_PropertyShapes_query)

        return shape_graph

    def generate_NodeShapes(self, shape_graph):

        generate_NodeShapes_query = """
prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
prefix sh:    <http://www.w3.org/ns/shacl#>
prefix shui:  <https://vocab.eccenca.com/shui/>
prefix owl:   <http://www.w3.org/2002/07/owl#>
prefix xsd:   <http://www.w3.org/2001/XMLSchema#>

CONSTRUCT {
  ?nodeShape a sh:NodeShape ;
    rdfs:label ?label ;
    sh:name ?name ;
    sh:targetClass ?class .
}
WHERE {
  ?res a ?class .
  BIND(IRI(CONCAT(STR(?class), "-NodeShape")) AS ?nodeShape)
  OPTIONAL { ?class rdfs:label ?classL . }
  BIND(REPLACE(STR(?class), ".*[/#]([^/#])", "$1") AS ?classLocal)
  BIND(IF(BOUND(?classL), STR(?classL), ?classLocal) AS ?label)
  BIND(STRLANG(CONCAT(?label, " Node Shape"), "en") AS ?name)
}
        """
        shape_graph += self.G.query(generate_NodeShapes_query)

        return shape_graph
