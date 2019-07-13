import json

from engine.repository.templates import InMemoryPopulatedTemplatesRepository
from engine.use_cases.parsing import ParsePopulatedTemplatesUseCase


def test_template_parser_use_case(resources):
    repo = InMemoryPopulatedTemplatesRepository(resources)
    parse_populated_templates_use_case = ParsePopulatedTemplatesUseCase(repo)
    result = parse_populated_templates_use_case.execute()
    assert (json.loads(result)["test_template.xlsx"]["data"]["Summary"]["B3"]
            == "This is a string")
