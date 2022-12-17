import json
from webapp.common.jsonenc import JsonEncoder
import webapp.api as API
from webapp.commands.exporter.base import DbExporter
from webapp.commands.exporter.yaml import YamlDbExporter


class JsonDbExporter( YamlDbExporter ):
    def close( self ):
        API.app.logger.info( "Writing the output file" )
        json.dump( self._blob, self._stream, indent = 4, cls = JsonEncoder )
        DbExporter.close( self )
        return
