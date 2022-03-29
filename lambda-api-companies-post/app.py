from pkgutil import extend_path
import boxsdk
from boxsdk import JWTAuth
import boto3
from itertools import zip_longest
import json
import numpy as np
import pandas as pd
import re
import typing as t
import unicodedata


def lambda_handler(event, context):
    extended_table = ExtendedTableGetter().get_table()
    # original_table = OriginalTableGetter().get_table()


    jwtauth = 'from_settings_file' in dir(JWTAuth)
    return {
        'boxsdk_version': boxsdk.__version__,
        'boto3_version': boto3.__version__,
        'pandas_version': pd.__version__,
        'jwtauth': jwtauth,
        'extended_table': extended_table,
    }


class ExtendedTableGetter:
    """
    Extracts and transforms table data from `extended-table.json`
    """
    def get_table(self):
        self._set_initial_table_data()
        self._set_columns_mapping()
        self._set_choices_mapping()
        return self._update_table_data_with_slugs(self._get_table_data())

    def _set_initial_table_data(self):
        with open('extended-table.json') as f:
            self.data = json.load(f)

    def _set_columns_mapping(self) -> t.Dict[str, str]:
        """
        Returns a mapping of Airtable internal field id to human readable field names
        """
        self._columns = {item['id']: item['name'] for item in self.data['table']['columns']}

    def _set_choices_mapping(self) -> t.Dict[str, str]:
        """
        Returns a mapping of Airtable internal id to human readable choice' names
        """
        self._choices = {}
        for item in self.data['table']['columns']:
            if item['typeOptions'] and 'choices' in item['typeOptions']:
                for choice_name, choice_vals in item['typeOptions']['choices'].items():
                    self._choices[choice_name] = choice_vals['name']
        return self._choices

    def _get_table_data(self) -> t.List[t.Dict[str, str]]:
        """
        Extracts table data into list of human readable dicts
        """
        return [{self._columns[header]: self._prepare_cell(cell)
            for header, cell in row['cellValuesByColumnId'].items()}
            for row in self.data['table']['rows'] if row.get('cellValuesByColumnId', {})]

    def _prepare_cell(self, cell: str) -> str:
        """
        Transforms value of a single cell to human readable flat format
        """
        if type(cell) == str and cell.startswith('sel'):
            return self._choices[cell]
        if type(cell) == list and 'url' in cell[0]:
            return cell[0]['url']
        return cell

    def _update_table_data_with_slugs(self,
            table_data: t.List[t.Dict[str, str]],
        ) -> t.List[t.Dict[str, str]]:
        """
        Iterates over list of dicts and adds a slug to each object
        """
        return [{**item, 'slug': slugify(item['Name'])} for item in table_data]


class OriginalTableGetter:
    """
    Extracts and transforms table data from the original Yale CELI list
    """
    def get_table(self):
        return


def slugify(value):
    """
    Converts to lowercase ascii, removes non-alphanumerics characters
    and converts spaces to hyphens. Also strips leading and
    trailing whitespaces.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)
