from boxsdk import Client
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
    original_table = OriginalTableGetter().get_table()


    jwtauth = 'from_settings_file' in dir(JWTAuth)
    return {
        # 'boxsdk_version': boxsdk.__version__,
        'boto3_version': boto3.__version__,
        'pandas_version': pd.__version__,
        'jwtauth': jwtauth,
        # 'extended_table': extended_table,
        'original_table': original_table,
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
        self._set_initial_table_data()
        self._add_status_column()
        self._fill_nulls_in_status_column()
        self._format_status_column()
        self._remove_rows_empty_in_Name_column()
        self._remove_rows_empty_in_Action_column()
        self._remove_header_row()
        self._remove_empty_columns()
        self._rename_columns()
        self._add_slug_column()
        return self._transform_pandas_df_to_list_of_dicts()

    def _set_initial_table_data(self) -> None:
        self.df = pd.read_excel('mock-original-table.xlsx', header=None, skiprows=1)
        del self.df[0] # temp

    def _add_status_column(self) -> None:
        """Add 'status' column retrieving string 'Withdrawal' from 
        '#1. WITHDRAWAL - Clean Break - Surgical Removal, Resection (174 Companies) (Grade: A)'"""
        regex_expr = r'((?<=^#\d. )[\w ]*(?<![ - ]))'
        self.df['status'] = self.df.iloc[:,0].str.extract(regex_expr, expand=False)

    def _fill_nulls_in_status_column(self) -> None:
        """Fill holes in 'status' column by propagating
        the last valid observation forward to next valid"""
        self.df['status'] = self.df['status'].fillna(method='ffill')

    def _format_status_column(self) -> None:
        """Format 'status' column"""
        self.df['status'] = self.df['status'].apply(lambda x: str(x).title().strip() if x else '')

    def _remove_rows_empty_in_Name_column(self) -> None:
        """Drop rows which are empty in 'Name' column"""
        self.df = self.df[self.df.iloc[:,0].notna()]

    def _remove_rows_empty_in_Action_column(self) -> None:
        """Drop rows which are empty in 'Action' column"""
        self.df = self.df[self.df.iloc[:,2].notna()]

    def _remove_header_row(self) -> None:
        """Drop header row ('Name', 'Logo', 'Action')"""
        self.df = self.df[(self.df.iloc[:,0] != 'Name') & (self.df.iloc[:,2] != 'Action')]

    def _remove_empty_columns(self) -> None:
        """Drop columns with only np.nan values"""
        self.df = self.df.dropna(axis=1, how='all')

    def _rename_columns(self) -> None:
        """Rename columns to 'name' and 'action'"""
        self.df = self.df.rename(columns={self.df.columns[0]: 'name', self.df.columns[1]: 'action'})

    def _add_slug_column(self) -> None:
        """"Add 'slug' column"""
        self.df['slug'] = self.df['name'].apply(lambda row: slugify(row))

    def _transform_pandas_df_to_list_of_dicts(self) -> t.List[t.Dict[str, str]]:
        """Convert the DataFrame to a list like 
        [{column -> value}, … , {column -> value}]"""
        return self.df[['name', 'action', 'status', 'slug']].to_dict('records')


def slugify(value):
    """
    Converts to lowercase ascii, removes non-alphanumerics characters
    and converts spaces to hyphens. Also strips leading and
    trailing whitespaces.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)
