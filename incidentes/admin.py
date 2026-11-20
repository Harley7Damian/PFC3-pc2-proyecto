from django.contrib import admin

from .models import Incidente


@admin.register(Incidente)
class IncidenteAdmin(admin.ModelAdmin):
    list_display = ("tipo", "distrito", "fecha_hecho", "visible")
    list_filter = ("tipo", "distrito", "visible")
    actions = ["ocultar", "mostrar"]

    @admin.action(description="Ocultar los reportes seleccionados")
    def ocultar(self, request, queryset):
        queryset.update(visible=False)

    @admin.action(description="Mostrar los reportes seleccionados")
    def mostrar(self, request, queryset):
        queryset.update(visible=True)
