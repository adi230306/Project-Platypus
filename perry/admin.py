from django.contrib import admin
from .models import CelestialProfile

@admin.register(CelestialProfile)
class CelestialProfileAdmin(admin.ModelAdmin):
    # Main list view columns
    list_display = (
        'name', 
        'celestial_type',
        'temperature',
        'has_rings',
        'moon_count',
        'base_response_delay',
        'gif_preview'
    )
    
    # Filtering options
    list_filter = (
        'celestial_type',
        'has_rings',
    )
    
    # Search functionality
    search_fields = ('name', 'celestial_type')
    
    # Grouped editing fields
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'celestial_type', 'gif')
        }),
        ('Physical Attributes', {
            'fields': ('temperature', 'has_rings', 'moon_count')
        }),
        ('Behavior', {
            'fields': ('base_response_delay', 'personality_prompt')
        }),
        ('Metadata', {
            'fields': ('image_url',),
            'classes': ('collapse',)
        })
    )
    
    # Custom methods
    def gif_preview(self, obj):
        return obj.gif.url if obj.gif else "No GIF"
    gif_preview.short_description = 'GIF Preview'