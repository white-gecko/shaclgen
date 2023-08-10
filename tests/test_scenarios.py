from rdflib import Graph
from shaclgen.schema import schema
from shaclgen.shaclgen import data_graph
from shaclgen.shaclgen_min import data_graph as data_graph_min
from shaclgen.shaclgen_query import data_graph as data_graph_query
from helpers import assertAskQuery
from os import listdir
from os.path import isfile, join
import yaml


def pytest_generate_tests(metafunc):
    scenarios = {
        "schema": {"class": schema, "sets": ["schema_default"]},
        "shaclgen": {"class": data_graph, "sets": ["data_min", "data_default"]},
        "shaclgen_min": {"class": data_graph_min, "sets": ["data_min"]},
        "shaclgen_query": {"class": data_graph_query, "sets": ["data_min"]},
    }
    idlist = []
    argvalues = []
    argnames = ["generator_class", "source_graph", "assertion_query", "init_args", "gen_graph_args"]
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
                idlist.append(f"{scenario[0]}_{test_set}_{test_name}")
                test_assertion_file = test_name + "_assertion.rq"
                test_data_file = test_name + "_data.ttl"
                test_config_file = test_name + "_config.yml"
                source_graph = Graph()
                source_graph.parse(join(test_data_dir, test_data_file), format="turtle")
                config = {}
                if isfile(join(test_data_dir, test_config_file)):
                    with open(join(test_data_dir, test_config_file), "r") as config_file:
                        try:
                            config = yaml.safe_load(config_file)
                        except yaml.YAMLError as exc:
                            print(exc)
                with open(join(test_data_dir, test_assertion_file), "r") as assertion_file:
                    argvalues.append(
                        [generator_class, source_graph, assertion_file.read(), config.get("init", {}) or {}, config.get("gen_graph", {}) or {}]
                    )
    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


class TestShapeGeneration:
    def test_shape_generation(self, generator_class, source_graph, assertion_query, init_args, gen_graph_args):
        extraction_graph = generator_class(source_graph, **init_args)
        shacl_graph = extraction_graph.gen_graph(**gen_graph_args)

        assertAskQuery(shacl_graph, assertion_query)
