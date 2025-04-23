from django.db import models
from datetime import date
from django.utils import timezone

class Recipe(models.Model):
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to='recipes/')
    ingredients = models.TextField("Ингредиенты", help_text="Один ингредиент в строку")
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    def __str__(self):
        return self.title

    @staticmethod
    def get_recipe_for_user(tg_user_id: int):

        record, _ = DailyRecipeLimit.objects.get_or_create(
            tg_user_id=tg_user_id,
            date=date.today(),
            defaults={'recipes_given': 0}
        )

        if record.recipes_given >= 33:
            return None

        recipe = Recipe.objects.filter(is_active=True).order_by('?').first()
        if recipe:
            record.recipes_given += 1
            record.last_recipe = recipe
            record.save()
        return recipe


class UserRecipeInteraction(models.Model):
    tg_user_id = models.BigIntegerField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tg_user_id', 'recipe')


class DailyRecipeLimit(models.Model):
    tg_user_id = models.BigIntegerField()
    date = models.DateField(default=timezone.now)
    recipes_given = models.IntegerField(default=0)
    last_recipe = models.ForeignKey('Recipe', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('tg_user_id', 'date')