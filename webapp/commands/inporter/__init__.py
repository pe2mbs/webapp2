from webapp.commands.inporter.base import DbInporters
from webapp.commands.inporter.csv import CsvDbInporter
from webapp.commands.inporter.sql import SqlDbInporter
from webapp.commands.inporter.yaml import YamlDbInporter
from webapp.commands.inporter.json import JsonDbInporter


dbInporters = DbInporters( { 'csv': CsvDbInporter,
                             'sql': SqlDbInporter,
                             'yaml': YamlDbInporter,
                             'json': JsonDbInporter } )


