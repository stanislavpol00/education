class ExportFilterSetMixin:
    export_filterset_class = None

    def get_export_queryset(self, request):
        queryset = super().get_export_queryset(request)
        if self.export_filterset_class:
            self.filterset = self.export_filterset_class(
                request.POST,
                queryset,
                request=request,
            )
            queryset = self.filterset.qs
        return queryset

    def get_export_context_data(self):
        data = super().get_export_context_data()
        if self.export_filterset_class:
            data["filterset"] = self.export_filterset_class()
        return data
