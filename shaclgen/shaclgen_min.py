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

        self.make_shapes(ng)

        return ng

    def format_namespace(self, iri):
        """
        add "/" to namespace if graph IRI does not end with "/" or "#"
        """
        return iri if iri.endswith(("/", "#")) else iri + "/"

    def get_name(self, iri):
        """
        get shape name, look up prefix at prefix.cc
        """
        qname = f"{self.namespaces.qname(iri)}"
        logger.debug(qname)
        return qname

    def get_class_dict(self):
        """
        get classes and properties
        """
        class_dict = {}
        query = f"""
        SELECT DISTINCT ?class ?property
        {{
            ?subject a ?class .
            ?subject ?property ?object .
        }}
        """  # nosec
        res = self.G.query(query)
        for binding in res:
            if binding["class"] not in class_dict:
                class_dict[binding["class"]] = {"fwd": [], "inv": []}
            class_dict[binding["class"]]["fwd"].append(binding["property"])
        query = f"""
        SELECT DISTINCT ?class ?property
        {{
            ?object a ?class .
            ?subject ?property ?object .
        }}
        """  # nosec
        res = self.G.query(query)
        for binding in res:
            if binding["class"] not in class_dict:
                class_dict[binding["class"]] = {"fwd": [], "inv": []}
            class_dict[binding["class"]]["inv"].append(binding["property"])

        return class_dict

    def make_shapes(self, shapes_graph):
        """
        make shapes
        """
        prop_uuids = []
        class_dict = self.get_class_dict()

        for cls, props in class_dict.items():
            cls_uuid = uuid5(NAMESPACE_URL, cls)
            node_shape_uri = URIRef(
                f"{self.format_namespace(self.shapes_graph_iri)}{cls_uuid}"
            )
            shapes_graph.add((node_shape_uri, RDF.type, SH.NodeShape))
            shapes_graph.add((node_shape_uri, SH.targetClass, URIRef(cls)))

            name = self.get_name(cls)
            shapes_graph.add((node_shape_uri, SH.name, Literal(name, lang="en")))

            fwds = len(props["fwd"])
            for i, prop in enumerate(props["fwd"] + props["inv"]):
                if i < fwds:
                    prop_uuid = uuid5(NAMESPACE_URL, prop)
                else:
                    prop_uuid = uuid5(NAMESPACE_URL, f"{prop}inverse")
                property_shape_uri = URIRef(
                    f"{self.format_namespace(self.shapes_graph_iri)}{prop_uuid}"
                )
                if prop_uuid not in prop_uuids:
                    shapes_graph.add((property_shape_uri, RDF.type, SH.PropertyShape))

                    name = self.get_name(prop)

                    if i >= fwds:
                        name += " (inverse)"
                        shapes_graph.add(
                            (property_shape_uri, SH.inversePath, Literal(True))
                        )
                    shapes_graph.add(
                        (property_shape_uri, SH.name, Literal(name, lang="en"))
                    )
                    shapes_graph.add((property_shape_uri, SH.path, URIRef(prop)))
                    prop_uuids.append(prop_uuid)
                shapes_graph.add((node_shape_uri, SH.property, property_shape_uri))

        return shapes_graph
