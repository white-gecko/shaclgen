from rdflib import Graph
from shaclgen.shaclgen import data_graph
from shaclgen.shaclgen_min import data_graph as data_graph_min
from shaclgen.shaclgen_query import data_graph as data_graph_query
from helpers import assertAskQuery
from os import listdir
from os.path import isfile, join


def pytest_generate_tests(metafunc):
    scenarios = {
        "shaclgen": {"class": data_graph, "sets": ["min", "default"]},
        "shaclgen_min": {"class": data_graph_min, "sets": ["min"]},
        "shaclgen_query": {"class": data_graph_query, "sets": ["min"]},
    }
    idlist = []
    argvalues = []
    argnames = ["generator_class", "source_graph", "assertion_query"]
    for scenario in scenarios.items():
        generator_class = scenario[1]["class"]
        for test_set in scenario[1]["sets"]:
            test_data_dir = "tests/testset_" + test_set
            test_names = [
                f[:-13]
                for f in listdir(test_data_dir)
                if isfile(join(test_data_dir, f)) and f.endswith("_assertion.rq")
            ]
            for test_name in test_names:
                idlist.append(scenario[0] + test_name)
                test_assertion_file = test_name + "_assertion.rq"
                test_data_file = test_name + "_data.ttl"
                source_graph = Graph()
                source_graph.parse(join(test_data_dir, test_data_file), format="turtle")
                with open(join(test_data_dir, test_assertion_file)) as assertion_file:
                    argvalues.append(
                        [generator_class, source_graph, assertion_file.read()]
                    )
    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


class TestShapeGeneration:
    def test_shape_generation(self, generator_class, source_graph, assertion_query):
        extraction_graph = generator_class(source_graph)
        shacl_graph = extraction_graph.gen_graph()

        assertAskQuery(shacl_graph, assertion_query)
