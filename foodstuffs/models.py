from django.db import models
from .utilities import get_timestamp_path


class Dimension(models.Model):          # full
    """Размерность - таблица храненит единицы измерения продуктов и
     предназначена для реализации фильтрации продуктов по допустимым
      единицам измерения (шт., гр, кг, ложки и т.д.)"""
    class Meta:
        ordering = ["short_name_dimension"]
        verbose_name = "Размерность"
        verbose_name_plural = "Размерности"

    short_name_dimension = models.CharField(max_length=50, verbose_name='сокращенное название размерности')
    full_name_dimension = models.CharField(max_length=100, verbose_name='полное название размерности')
    description_dimension = models.TextField(max_length=200, null=True, blank=True)


class TypeProducts(models.Model):       # full
    """Тип продуктов. Для реализации сортировки и группировки продуктов"""
    class Meta:
        ordering = ["name_type_product"]
        verbose_name = "Тип продуктов"
        verbose_name_plural = "Типы продуктов"

    name_type_product = models.CharField(max_length=50, verbose_name='тип продуктов')


class Products(models.Model):           # full
    """ Продукты - хранения наименований продуктов для
    формирования ингредиентов в рецептах """
    class Meta:
        ordering = ["name_product"]
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    name_product = models.CharField(max_length=70, verbose_name='название продукта')
    kcal_product = models.PositiveIntegerField(null=True, blank=True, verbose_name='Килокаллории')
    type_product = models.ForeignKey(TypeProducts, on_delete=models.PROTECT, verbose_name='тип продукта')


class TypeRecipes(models.Model):
    """Типы рецептов"""
    name_type_recipes = models.CharField(max_length=70)
    super_type_recipe = models.ForeignKey("SuperTypeRecipes", on_delete=models.PROTECT,
                                          null=True, blank=True, verbose_name='Надтип рецептов')
    description_type_recipes = models.TextField(max_length=300)


class SuperTypeRecipesManager(models.Manager):
    """Диспетчер записей для особой фильтрации подтипов по надтипам"""
    def get_queryset(self):
        return super().get_queryset().filter(super_type_recipe__isnull=True)


class SuperTypeRecipes(TypeRecipes):
    """Прокси модель для создания структуры надтипов.
    Задаем диспетчер записей SuperTypeRecipesManager"""
    objects = SuperTypeRecipesManager()

    # Метод который генерирует строковое представление надтипа (ее название)
    def __str__(self):
        return self.name_type_recipes

    class Meta:
        proxy = True
        ordering = ["name_type_recipes"]
        verbose_name = "Надтип рецептов"
        verbose_name_plural = "Надтипы рецептов"


class SubTypeRecipesManager(models.Manager):
    """Диспетчер записей для особой фильтрации подтипов по надтипам"""
    def get_queryset(self):
        return super().get_queryset().filter(super_type_recipe__isnull=False)


class SubTypeRecipes(TypeRecipes):
    """Прокси модель для создания структуры подтипов.
    Задаем диспетчер записей SubTypeRecipesManager"""
    objects = SubTypeRecipesManager()

    # Метод который генерирует строковое представление надтипа (ее название)
    def __str__(self):
        return '%s - %s' % (self.super_type_recipe.name, self.name_type_recipes)

    class Meta:
        proxy = True
        ordering = ["super_type_recipe__name_type_recipes", "name_type_recipes"]
        verbose_name = "Подтип рецептов"
        verbose_name_plural = "Подтипы рецептов"


class Recipes(models.Model):            # full
    """Хранение рецептов"""
    class Meta:
        ordering = ["name_recipe"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    name_recipe = models.CharField(max_length=70, verbose_name='Название рецепта')
    type_recipes = models.ForeignKey(TypeRecipes, on_delete=models.PROTECT, verbose_name='Тип рецепта')
    description_recipe = models.TextField(max_length=300, verbose_name='Описание рецепта')
    photo_of_recipe = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='Избражение рецепта')


class Ingredients(models.Model):            # full
    """ Ингредиенты - перечень ингредиентов для рецепта"""
    class Meta:
        ordering = ["name_ingredient"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    name_ingredient = models.ForeignKey(Products, on_delete=models.PROTECT, verbose_name='название ингредиента')
    recipe_ingredient = models.ForeignKey(Recipes, on_delete=models.CASCADE, verbose_name='рецепт')
    dimension_ingredient = models.ForeignKey(Dimension, on_delete=models.PROTECT, verbose_name='размерность')
    number_of_ingredient = models.PositiveIntegerField(verbose_name='количество')


class StepsOfCooking(models.Model):             # full
    """Этапы/шаги приготовления рецепта"""
    class Meta:
        ordering = ["order_step"]
        verbose_name = "Этап приготовления"
        verbose_name_plural = "Этапы приготовления"

    order_step = models.PositiveIntegerField(default=0, db_index=True, verbose_name='Порядок')
    step_cooking = models.TextField(max_length=300, verbose_name='Этап приготовения')
    time_cooking = models.TimeField(null=True, blank=True, verbose_name='Время выполнения этапа')
    photo_of_step = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='Избражение')
    recip_for_steps = models.ForeignKey(Recipes, on_delete=models.CASCADE, verbose_name='рецепт')
