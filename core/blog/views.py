from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView  
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import F, Q, Count
from django.urls import reverse_lazy
from .models import Post, Category, Tag, Comment, Like
from .forms import PostForm, CommentForm

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, 'شما دسترسی به این بخش را ندارید!')
        return redirect('blog:blog_home')

class PostList(ListView):
    template_name = 'blog/blog-home.html'
    context_object_name = 'posts'
    model = Post
    queryset = Post.objects.filter(status=True).annotate(
        likes_count=Count('likes'),
        comments_count=Count('comments')
    )
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()

        category_slug = self.request.GET.get('category', '')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['current_category'] = self.request.GET.get('category', '')
        return context

class Post_detail(DetailView):
    model = Post
    template_name = 'blog/blog-single.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comments'] = post.comments.all()
        context['comment_form'] = CommentForm()
        context['likes_count'] = post.likes.count()

        if self.request.user.is_authenticated:
            context['user_liked'] = post.likes.filter(user=self.request.user).exists()

        if post.category:
            context['related_posts'] = Post.objects.filter(
                status=True, 
                category=post.category
            ).exclude(id=post.id)[:3]
        else:
            context['related_posts'] = Post.objects.filter(
                status=True
            ).exclude(id=post.id)[:3]
        return context

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        session = self.request.session
        key = f"viewed_post_{post.id}"

        if not session.get(key, False):
            Post.objects.filter(pk=post.pk).update(views=F('views') + 1)
            post.refresh_from_db(fields=['views'])
            session[key] = True
            session.modified = True
        return post

@method_decorator(staff_member_required, name='dispatch')
class PostCreateView(CreateView):
    model = Post
    fields = ['title', 'content', 'image', 'status', 'category']
    template_name = 'blog/create_post.html'
    success_url = reverse_lazy('blog:blog_home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = True
        response = super().form_valid(form)

        tags_str = self.request.POST.get('tags', '')
        if tags_str:
            tags_list = [t.strip() for t in tags_str.split(',') if t.strip()]
            for tag_name in tags_list:
                tag_obj, created = Tag.objects.get_or_create(name=tag_name)
                form.instance.tags.add(tag_obj)

        messages.success(self.request, 'پست شما با موفقیت ایجاد شد.')
        return response

@method_decorator(staff_member_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/edit_post.html'
    context_object_name = 'post'

    def get_success_url(self):
        return reverse_lazy('blog:blog_home')

@method_decorator(staff_member_required, name='dispatch')
class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/confirm_delete.html'
    context_object_name = 'post'
    success_url = reverse_lazy('blog:blog_home')

class AddCommentView(LoginRequiredMixin, DetailView):
    model = Post
    context_object_name = 'post'

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'کامنت شما با موفقیت ثبت شد.')
        else:
            messages.error(request, 'خطا در ثبت کامنت.')
        
        return redirect('blog:post_detail', pk=post.pk)
    
class ToggleLikeView(LoginRequiredMixin, DetailView):
    model = Post

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        user = request.user
        like, created = Like.objects.get_or_create(post=post, user=user)
        
        if not created:
            like.delete()
            messages.info(request, 'لایک شما حذف شد.')
        else:
            messages.success(request, 'پست لایک شد!')
        
        return redirect('blog:post_detail', pk=post.pk)