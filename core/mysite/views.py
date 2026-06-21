from django.shortcuts import render
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from blog.models import Post
from .forms import ContactForm
from .models import ContactMessage

class HomePageView(TemplateView):
    template_name = 'mysite/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_posts'] = Post.objects.filter(status=True).order_by('-views')[:3] 
        return context

class ContactUsView(FormView):
    template_name = "mysite/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("mysite:contact")

    def form_valid(self, form):
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        message = form.cleaned_data["message"]
        subject = form.cleaned_data["subject"]

        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message,
            subject=subject
        )
        messages.success(self.request, "پیام شما با موفقیت ارسال شد")
        return super().form_valid(form)

def about_view(request):
    context = {
        'total_posts': Post.objects.filter(status=True).count(),
        'total_categories': __import__('blog.models', fromlist=['Category']).Category.objects.count(),
    }
    return render(request, 'mysite/about.html', context)

def custom_404(request, exception):
    return render(request, '404.html', status=404)