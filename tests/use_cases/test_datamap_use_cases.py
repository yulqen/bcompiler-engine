from engine.repository.datamap import InMemorySingleDatamapRepository
from engine.use_cases.parsing import ParseDatamapUseCase


def test_parse_datamap_to_in_memory_use_case(datamap,
                                             datamapline_list_objects):
    # repo is a InMemorySingleDatamapRepository here
    repo = InMemorySingleDatamapRepository(datamap)
    parse_datamap_use_case = ParseDatamapUseCase(repo)
    result = parse_datamap_use_case.execute()

    assert result[0].key == datamapline_list_objects[0].key
