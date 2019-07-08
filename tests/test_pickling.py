import hashlib

from engine.parser import get_xlsx_files, hash_target_files, template_reader


def test_hash_of_target_files(resources):
    test_file_name = "test_template.xlsx"
    excel_files = get_xlsx_files(resources)
    test_file = [x for x in excel_files if x.name == test_file_name][0]
    digest_of_test_file = hashlib.md5(open(test_file, "rb").read()).digest()
    get_hashes = hash_target_files(excel_files)
    computed_hash = get_hashes[test_file_name]
    assert digest_of_test_file == computed_hash


def test_pickle_extracted_data_from_single_file(template):
    # dataset = template_reader(template)
    # TODO - finish this
    pass
