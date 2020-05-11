#!/usr/bin/env python3




import os
from docutils.core import publish_string


class Reader:

    def __init__(self, data_path: str = os.path.join("static", "texts")):

        self.data_path = data_path
        assert all([file in os.listdir(self.data_path) for file in ["about.rst", "tech_details.rst", "links.rst"]]), "Missing file in static text data."

    @staticmethod
    def rst_to_html(rst_string: str):
        return publish_string(rst_string, writer_name='html')

    @staticmethod
    def read_rst(rst_path: str):
        with open(rst_path, "r") as handler:
            data = handler.read()
        return data

    def get_text(self, page):
        """ Text should be got from rst files not in plain HTML """
        rst_data = self.read_rst(rst_path=os.path.join(self.data_path, f"{page}.rst"))
        html_data = self.rst_to_html(rst_string=rst_data)
        # Remove \n tag
        html_data = str(html_data.decode()).replace("\\n", "</ BR>")
        return html_data
