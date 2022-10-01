from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Profile)


class DumplingAdmin(admin.ModelAdmin):
    list_display = ('name', 'photo', 'slug')
    list_filter = ('meat', 'size', 'tasty')
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name',)}  # this creates the slug field from the title field
    autocomplete_fields = ('meat', 'size', 'tasty')


admin.site.register(Dumpling, DumplingAdmin)


# DumplingMeatAdmin must define "search_fields", because it's referenced by DumplingAdmin.autocomplete_fields.
class DumplingMeatAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(DumplingMeat, DumplingMeatAdmin)


class DumplingSizeAdmin(admin.ModelAdmin):
    search_fields = ('size',)


admin.site.register(DumplingSize, DumplingSizeAdmin)


class DumplingTastyAdmin(admin.ModelAdmin):
    search_fields = ('taste',)


admin.site.register(DumplingTasty, DumplingTastyAdmin)


@admin.register(DumplingComment)
class DumplingCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'dumpling', 'comment', 'time_create', 'time_update', 'is_published', 'bad_status')
    filter_horizontal = ('likes',)
    list_filter = ('is_published', 'time_create', 'likes')
    search_fields = ('comment', 'author', 'dumpling')
    actions = ['approve_comments', 'ban_comment']

    def approve_comments(self, request, queryset):
        queryset.update(is_published=True)

    def ban_comment(self, request, queryset):
        print(queryset)
        for comment in queryset:
            comment.author.profile.up_chort_status()
            comment.author.profile.save()

        queryset.update(is_published=False)
