from django.shortcuts import render, redirect
from .models import Article
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _
from Users.utils import pagination



class ArticleView(LoginRequiredMixin, View):
    """ Main view """

    templates_name = 'article-view.html'

    articles = Article.objects.all().order_by('id')

    page = 'article-view/'

    context = {
        'articles': articles,
        'page' : page
    }

    def get(self, request, *args, **kwargs):

        items = pagination(request, self.articles)

        self.context['articles'] = items

        return render(request, self.templates_name, self.context)
    
    
    def post(self, request, *args, **kwargs):


        # deleting a Article

        if request.POST.get('id_supprimer'):

            try:

                obj = Article.objects.get(pk = request.POST.get('id_supprimer'))
                obj.delete()

                messages.success(request, _("The deletion was successful."))
            
            except Exception as e:

                messages.error(request, f"Sorry, the following error has occurred {e}.")

        items = pagination(request, self.articles)

        self.context['articles'] = items

        return render(request, self.templates_name, self.context)
    

class AddArticleView(LoginRequiredMixin, View):
    """ add new article """

    page = 'add-article/'

    context = {
        'page' : page
    }
    # templates_name = ''

    def get(self, request, *args, **kwargs):

        if request.user.role == 'M':
            templates_name = 'manager/add-article.html'

        else:
            templates_name = 'add-article.html'


        return render(request, templates_name, self.context)

    def post(self, request, *args, **kwargs):

        if request.user.role == 'M':
            templates_name = 'manager/add-article.html'
        
        else:
            templates_name = 'add-article.html'

        data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'quantity': request.POST.get('quantity'),
            'unit_price': request.POST.get('unit_price'),
            'date_per': request.POST.get('date_per'),
            'image_url': request.POST.get('image_url'),
            'save_by': request.user
        }

        if not data['date_per']:
            data['date_per'] = None

        try:
            created = Article.objects.create(**data)

            if created:
                messages.success(request, _("article registered successfully."))
                
                if request.user.role == 'M':
                    return redirect('manager-dashboard')
                else:
                    return redirect('article-view')

            else:
                messages.error(request, "sorry, pleace try again, the sent data is corrupt.")

        except Exception as e:
            messages.error(request, f"Sorry our system is detecting the following issues {e}.")

        return render(request, templates_name)




class UpdateArticleView(LoginRequiredMixin, View):
    """ View to update an existing inArticle"""

    # template_name = 'update-article.html'

    def get(self, request, pk, *args, **kwargs):
        try:
            article = Article.objects.get(id=pk)
            page = f'update-article/{pk}/'

            context = {
                'article': article,
                'page': page
            }

            if request.user.role == 'M':
                templates_name = 'manager/update-article.html'

            else:
                templates_name = 'update-article.html'

            return render(request, templates_name, context)
        
        except Article.DoesNotExist:
            messages.error(request, "Article not found.")
            return redirect('article-view')

    def post(self, request, pk, *args, **kwargs):
        try:
            article = Article.objects.get(id=pk)


            

            # Mise à jour des champs de l'objet Article
            article.name = request.POST.get('name')
            article.description = request.POST.get('description')
            article.date_per = request.POST.get('date_per')
            article.unit_price = request.POST.get('unit_price')
            article.quantity = request.POST.get('quantity')
            article.image_url = request.POST.get('image_url')
        
            if not article.date_per:
                article.date_per= None

            article.save()

            messages.success(request, _("Article updated successfully."))

            if request.user.role == 'M':
                return redirect('manager-dashboard')
            else:
                return redirect('article-view')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('update-article', pk=pk)

