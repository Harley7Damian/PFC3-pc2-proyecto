from django.contrib import admin

from .models import Estacionamiento


@admin.register(Estacionamiento)
class EstacionamientoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "distrito", "tipo", "aprobado")
    list_filter = ("aprobado", "distrito", "tipo")
    actions = ["aprobar"]

    @admin.action(description="Aprobar los registros seleccionados")
    def aprobar(self, request, queryset):
        queryset.update(aprobado=True)
