import json

from engine.domain.template import TemplateCell
from engine.serializers.template import (ParsedTemplatesSerializer,
                                         TemplateCellSerializer)
from engine.use_cases.parsing import DatamapLineValueType


def test_template_cell_to_dict(template_cell_obj):
    assert template_cell_obj.to_dict()["sheet_name"] == "Test Sheet 1"


def test_template_cell_serializer(template_cell_obj):
    # TODO - test the ParsedTemplatesSerializer which is the multiple one
    json_output = json.dumps(template_cell_obj, cls=TemplateCellSerializer)
    assert json.loads(json_output)["sheet_name"] == "Test Sheet 1"
