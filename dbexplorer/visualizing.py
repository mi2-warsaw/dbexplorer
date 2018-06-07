from typing import Mapping
from os import path
import simplejson as json

FLOAT_PRECISION = 3


def pretty_floats(obj):
    """
    Converting floats in json data to proper form
    :param obj:
    :return:
    """
    if isinstance(obj, float):
        return f"{obj:.{FLOAT_PRECISION}f}"
    elif isinstance(obj, dict):
        return dict((k, pretty_floats(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return list(map(pretty_floats, obj))
    return obj


class DbVisualizer:
    """
    Visualizing extracted database data as HTML file
    """

    TEMPLATE_DIR = path.join(path.dirname(__file__))

    def __init__(self, data: Mapping, out_path: str):
        """
        :param data: extracted db data
        :param out_path: output path of created file
        """
        self.data = data
        self.out_path = out_path

    def generate_report(self) -> None:
        """
        creating report from data
        """
        template = DbVisualizer._get_template_file('template/template.html')

        data_js = DbVisualizer._get_template_file('template/data.js')
        controls = DbVisualizer._get_template_file('template/controls.js')
        table = DbVisualizer._get_template_file('template/table.js')
        results_module = DbVisualizer._get_template_file('template/resultsModule.js')
        search_module = DbVisualizer._get_template_file('template/searchModule.js')
        app = DbVisualizer._get_template_file('template/app.js')

        styles = DbVisualizer._get_template_file('template/styles.css')

        data_js = data_js.replace('{{data}}',
                                  json.dumps(pretty_floats(self.data), ensure_ascii=False, use_decimal=True))

        scripts = data_js + controls + table + results_module + search_module + app

        html = template.replace('{{scripts}}', scripts).replace('{{styles}}', styles)
        with open(self.out_path, 'w', encoding='utf-8') as fh:
            fh.write(html)

    @staticmethod
    def _get_template_file(file_path: str) -> str:
        """
        Loading template files
        :param file_path: single file path
        :return: template data
        """
        with open(path.join(DbVisualizer.TEMPLATE_DIR, file_path), 'r', encoding='utf-8') as fh:
            content = fh.read()
            fh.close()
        return content
