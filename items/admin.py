from django.contrib import admin
from .models import Food
from user.models import Disease
@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    # Displays neat columns in the admin panel table list
    list_display = ('variant', 'item', 'type')
    


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'f2avoid')
    search_fields = ('name', 'symptoms', 'medicines')