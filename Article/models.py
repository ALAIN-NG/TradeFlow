from django.db import models
from Users.models import Person

class Article(models.Model):
    """
    Name: Article model definition
    Description:
    Author: alaingildasngueudjang@gmail.com
    """

    save_by = models.ForeignKey(
        Person,
        related_name='manager_articles',
        on_delete=models.PROTECT,
        limit_choices_to={'role': 'M'},  # Filter to make sure the person is a Manager
    )

    name = models.CharField(max_length=100)

    description = models.CharField(max_length=255)

    quantity = models.IntegerField()

    unit_price = models.DecimalField(max_digits=1000, decimal_places=2)

    date_per = models.DateField(blank=True, null=True)

    image_url = models.ImageField(blank=True, upload_to= 'img')

    class Meta:

        constraints = [
            models.UniqueConstraint(fields=['name'], name = 'unique_article_name')
        ]
        verbose_name = "Article"
        verbose_name_plural = "Articles"
    
    def __str__(self):
        return f"{self.name}"

    def get_prix(self):
        return self.unit_price
    
    def set_price(self, new_price):
        self.unit_price = new_price
        self.save()

