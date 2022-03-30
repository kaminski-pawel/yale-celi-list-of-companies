# from boxsdk import Client
# from boxsdk import JWTAuth
import boto3
import bs4
from itertools import zip_longest
import json
# import numpy as np
# import pandas as pd
import re
import requests
import typing as t
import unicodedata


def lambda_handler(event, context):
    extended_table = ExtendedTableGetter().get_table()
    original_table = OriginalTableGetter().get_table()
    table = join_on_key(extended_table, original_table, join_on='slug')
    return {
        'table': table
    }


class ExtendedTableGetter:
    """
    Extracts and transforms table data from `extended-table.json`
    """

    def __init__(self):
        self._prefix = 'e_' # 'e' as in 'extended'

    def get_table(self):
        self._set_initial_table_data()
        self._set_columns_mapping()
        self._set_choices_mapping()
        return self._update_table_data_with_slugs(self._get_table_data())

    def _set_initial_table_data(self) -> None:
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
        return [{self._prepare_header(header): self._prepare_cell(cell)
            for header, cell in row['cellValuesByColumnId'].items()}
            for row in self.data['table']['rows'] if row.get('cellValuesByColumnId', {})]

    def _prepare_header(self, header: str) -> str:
        """Transforms 'Market Cap' to 'e_market_cap' str (except 'slug' field)"""
        _header = self._columns[header].lower().strip()
        if _header == 'slug':
            return _header
        return self._prefix + _header.replace(' ', '_')

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
        return [{**item, 'slug': slugify(item['e_name'])} for item in table_data]


class OriginalTableGetter:
    """
    Extracts and transforms table data from Yale website
    """

    def __init__(self):
        self._prefix = 'orig_'
        self._source_url = 'https://som.yale.edu/story/2022/over-450-companies-have-withdrawn-russia-some-remain'

    def get_table(self):
        soup = self._parse_html(self._fetch_html())
        return self._flatten_tables_into_one(self._get_multiple_tables(soup))

    def _fetch_html(self) -> bytes:
        return requests.get(self._source_url).content

    def _parse_html(self,
            markup: bytes,
        ) -> bs4.BeautifulSoup:
        """Represent html docment as a nested structure"""
        return bs4.BeautifulSoup(markup, 'html.parser')

    def _get_multiple_tables(self,
            soup: bs4.BeautifulSoup,
        ) -> t.List[t.List[t.Dict[str, str]]]:
        """Iterates over <section> tags, extracts and transforms tables.
        Tables are nested: [[{}, {}], [{}, {}]]"""
        final_table = []
        for html_elem in self._get_html_sections_with_tables(soup):
            headers = self._get_headers(html_elem)
            table = self._extract_table(html_elem, headers)
            final_table.append(self._transform_table(html_elem, table))
        return final_table

    def _get_html_sections_with_tables(self,
            soup: bs4.BeautifulSoup,
        ) -> t.List[bs4.element.Tag]:
        return soup.findAll('section', {'class': 'layout layout--one-column'})

    def _prepare_header(self, header: str, prefix: str = '') -> str:
        """Converts '\ufeffName' to 'someprefix_name' str (except 'slug' field)"""
        s = header.strip().lower()
        s = s.replace('\ufeff', '')
        return s if s == 'slug' else prefix + s

    def _get_headers(self,
            tag_elem: bs4.element.Tag,
        ) -> t.List[str]:
        """Returns ['header1', 'header2'] from <th> tags"""
        return [self._prepare_header(th.getText(), prefix=self._prefix)
                for th in tag_elem.findAll('th')]

    def _extract_tablerow(self,
            tr: bs4.element.Tag,
            headers: t.List[t.Dict[str, str]],
        ) -> t.Dict[str, str]:
        """Returns {'header1': 'valFromTD1', 'header2': 'valFromTD2'} object"""
        return dict(zip(headers, [td.getText() for td in tr.findAll('td')]))

    def _extract_table(self,
            tag_elem: bs4.element.Tag,
            headers: t.List[t.Dict[str, str]],
        ) -> t.List[t.Dict[str, str]]:
        """Returns list of unprocessed tablerows"""
        return [self._extract_tablerow(tr, headers) for tr in tag_elem.findAll('tr')]

    def _transform_table(self,
            tag_elem: bs4.element.Tag,
            table: t.List[t.Dict[str, str]],
        ) -> t.List[t.Dict[str, str]]:
        """Omits empty rows and adds additional fields"""
        return [{
            **row,
            **self._get_status_field(tag_elem),
            **self._get_slug_field(row),
        } for row in table if row]

    def _get_status_field(self,
            tag_elem: bs4.element.Tag,
        ) -> t.Dict[str, str]:
        """Returns dictionary for status: e.g. {'status': 'scalingback'}"""
        return {self._prefix + 'status': tag_elem.attrs.get('id')}

    def _get_slug_field(self,
            row: t.Dict[str, str],
        ) -> t.Dict[str, str]:
        return {'slug': slugify(row.get(self._prefix + 'name'))}

    def _flatten_tables_into_one(self,
            multiple_tables: t.List[t.List[t.Dict[str, str]]]
        ) -> t.List[t.Dict]:
        """Transforms [[{}, {}], [{}, {}]] into [{}, {}, {}, {}]"""
        return [row for tbl in multiple_tables for row in tbl]


def slugify(value: str) -> str:
    """
    Converts to lowercase ascii, removes non-alphanumerics characters
    and converts spaces to hyphens. Also strips leading and
    trailing whitespaces.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)

def join_on_key(
        l1: t.List[t.Dict[str, t.Any]],
        l2: t.List[t.Dict[str, t.Any]],
        join_on: str,
    ) -> t.List[t.Dict[str, t.Any]]:
    """
    Create one big dictionary where the `join_on` value serves as a dict key,
    merging values of two lists of dictionaries, `l1` and `l2`. 
    Return as a list of merged dictionaries.
    """
    d1 = {d[join_on]:d for d in l1}
    return [dict(d, **d1.get(d[join_on], {})) for d in l2]
