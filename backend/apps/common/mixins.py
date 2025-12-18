from rest_framework.decorators import action
from .excel import ExcelUtil

class ExportExcelMixin:
    """
    Mixin to add export action to ViewSet.
    Requires `export_field_label` (dict) or `export_fields` (list) and `export_headers` (list) 
    to be defined in ViewSet.
    """
    
    @action(detail=False, methods=['post'])
    def export(self, request, *args, **kwargs):
        # Filter queryset based on request params (search, etc.)
        queryset = self.filter_queryset(self.get_queryset())
        
        # Determine fields and headers
        field_list = getattr(self, 'export_fields', [])
        header_list = getattr(self, 'export_headers', [])
        
        # If export_field_label dict is provided, use it (OrderedDict recommended for order)
        export_field_label = getattr(self, 'export_field_label', None)
        if export_field_label:
            field_list = list(export_field_label.keys())
            header_list = list(export_field_label.values())
            
        if not field_list:
            # Fallback to serializer fields if not configured
            serializer_class = self.get_serializer_class()
            if serializer_class:
                try:
                    # Get all fields from serializer
                    fields = serializer_class().fields
                    field_list = list(fields.keys())
                    header_list = [f.label or f.source or k for k, f in fields.items()]
                except Exception:
                    pass
        
        if not field_list:
            from rest_framework.response import Response
            return Response({'code': 500, 'msg': '未配置导出字段'})
            
        excel = ExcelUtil(queryset, field_list, header_list)
        filename = getattr(self, 'export_filename', 'export')
        return excel.export_excel(filename)
