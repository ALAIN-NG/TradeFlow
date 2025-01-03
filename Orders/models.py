from django.db import models
from django.utils.translation import gettext_lazy as _
from Users.models import Person
from Article.models import Article

class Invoice(models.Model):
    """
    Name: Invoice model definition
    Description: 
    author: alaingildasngueudjang@gmail.com
    """


    INVOICE_TYPE = (
        ('R', _('RECEIPT')),
        ('P', _('PROFORMA INVOICE')),
        ('I', _('INVOICE')),
    )

    customer = models.ForeignKey(
        Person,
        related_name='customer_invoices',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'C'},  # Filter to make sure the person is a customer
    )

    save_by = models.ForeignKey(
        Person,
        related_name='seller_invoices',
        on_delete=models.CASCADE,
        limit_choices_to={'role': ['S', 'A', 'C']},  # Filter to make sure the person is a seller
    )

    invoice_date_time = models.DateTimeField(auto_now_add=True)

    total = models.DecimalField(max_digits=10000, decimal_places=2)

    paid = models.BooleanField(default=False)

    invoice_type = models.CharField(max_length=1, choices=INVOICE_TYPE)

    comments = models.TextField(null=True, max_length=1000, blank=True)

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self):
        return f"{self.customer.name}_{self.invoice_date_time}"

    @property
    def get_total(self):
        articles = self.order_line_set.all()
        total = sum(article.get_total for article in articles)
        return total
        

    @property 
    def get_panier_total(self):
        """ prix total des articles dans le panier"""
        articles = self.order_line_set.all()
        total = sum([article.get_total for article in articles])
        return total  

    @property
    def get_panier_article(self):
        """ Nombre total des articles dans le panier"""
        articles = self.order_line_set.all()
        quantite_total = sum([article.quantity for article in articles])
        return quantite_total



class Order_line(models.Model):
    """
    Name: Order_line model definition
    Description:
    Author: alaingildasngueudjang@gmail.com
    """

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

    article_name = models.ForeignKey(Article, related_name='article', on_delete=models.PROTECT)

    quantity = models.IntegerField()

    unit_price = models.DecimalField(max_digits=1000, decimal_places=2)

    total = models.DecimalField(max_digits=1000, decimal_places=2)


    class Meta:
        verbose_name = "Order_line"
        verbose_name_plural = "Order_lines"

    @property
    def get_total(self):
        total = self.quantity * self.unit_price 
        return total
