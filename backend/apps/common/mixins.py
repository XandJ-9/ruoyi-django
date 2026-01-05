from rest_framework.decorators import action
from rest_framework.response import Response
from urllib.parse import quote
from apps.utils import ExcelUtil

class BaseViewMixin:
    # 通用响应封装
    def ok(self, msg='操作成功'):
        return Response({'code': 200, 'msg': msg})

    def error(self, msg='操作失败'):
        return Response({'code': 400, 'msg': msg})
    
    def data(self, data, msg='操作成功'):
        return Response({'code': 200, 'msg': msg, 'data': data})

    def not_found(self, msg='未找到'):
        return Response({'code': 404, 'msg': msg})
    
    def raw_response(self, data):
        return Response(data)

    def csv_response(self, columns, rows, filename, bom=False):
        import csv, io
        from django.http import HttpResponse
        output = io.StringIO()
        if bom:
            output.write('\ufeff')
        if columns:
            headers = columns
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            for r in rows:
                row = {k: v for k, v in zip(headers, r)}
                writer.writerow(row)
        resp = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = f'attachment; filename={quote(filename)}'
        return resp

    def excel_response(self, filename, workbook):
        # Ensure filename has extension
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        # 使用传入的 openpyxl.Workbook 生成 xlsx 响应
        import io
        from django.http import HttpResponse
        try:
            output = io.BytesIO()
            workbook.save(output)
        except Exception as e:
            return self.error(f'导出 Excel 失败：{e}')
        resp = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = f'attachment; filename={quote(filename)}'
        return resp

class ExportExcelMixin(BaseViewMixin):
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
            
        # excel = ExcelUtil(queryset, field_list, header_list)
        # filename = getattr(self, 'export_filename', 'export')
        # return excel.make_excel(filename)
        excel = ExcelUtil(queryset, field_list, header_list)
        filename = getattr(self, 'export_filename', 'export')
        wb = excel.make_excel(filename)
        return self.excel_response(filename, wb)
