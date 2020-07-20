from django.contrib import admin
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import path
from openpyxl.writer.excel import save_virtual_workbook

from processlogs.apps.apachelogs import utils as apachelogs_utils
from processlogs.apps.apachelogs.models import ApacheLog, BrokenLog


@admin.register(ApacheLog)
class ApacheLogAdmin(admin.ModelAdmin):
    list_display = ('ipv4_address', 'date_logged', 'http_method', 'url', 'status_code', 'content_length')
    list_display_links = None
    readonly_fields = ('ipv4_address', 'date_logged', 'http_method', 'url', 'status_code', 'content_length')
    fields = ('ipv4_address', 'date_logged', 'http_method', 'status_code', 'content_length')
    search_fields = ['ipv4_address', 'url']
    list_filter = ('http_method', 'status_code')
    ordering = ('-date_logged', )
    sortable_by = list_display
    actions = None
    list_per_page = 30
    change_list_template = 'my_admin/change_list.html'
    queryset = None

    def changelist_view(self, request, extra_context=None):
        template = super(ApacheLogAdmin, self).changelist_view(request)
        self.queryset = template.context_data['cl'].queryset

        aggr_data = self.queryset.aggregate(Count('ipv4_address', distinct=True), Count('http_method', distinct=True),
                                            byte_sum=Coalesce(Sum('content_length'), 0))

        template.context_data['ip_count'] = aggr_data['ipv4_address__count']
        template.context_data['methods_count'] = aggr_data['http_method__count']
        template.context_data['byte_sum'] = aggr_data['byte_sum']
        template.context_data['top_ip_addresses'] = self.queryset.values('ipv4_address').annotate(
            total=Count('ipv4_address')
        ).order_by('-total')[:10]
        return template

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('report/', self.report),
        ]
        return my_urls + urls

    def report(self, request):
        if not self.queryset:
            return HttpResponseRedirect("../")

        report = apachelogs_utils.report(self.queryset)
        self.message_user(request, "Отчет создан")
        response = HttpResponse(content=save_virtual_workbook(report),
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=Report.xlsx'

        return response


@admin.register(BrokenLog)
class BrokenLogAdmin(admin.ModelAdmin):
    list_display = ('text',)
    list_per_page = 30
    list_display_links = None
    actions = None
    change_list_template = None

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
