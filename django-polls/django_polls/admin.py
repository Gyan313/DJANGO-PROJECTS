from django.contrib import admin

# Register your models here.

from .models import Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


# customizing the admin site of django..
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        (
            "Date Informantion",
            {"fields": ["published_date"], "classes": ["collapse"]},
        ),
    ]
    inlines = [ChoiceInline]

    @admin.display(description="#Choices")
    def number_of_choices(self, obj):
        return f"{obj.choice_set.count()}"

    list_display = ["question_text", "published_date", "number_of_choices"]

    list_filter = ["published_date"]

    search_fields = ["question_text"]


admin.site.register(Question, QuestionAdmin)
