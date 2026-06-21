from django import forms
from .models import Post, Category, Tag, Comment

class PostForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        help_text="Separate tags with commas (e.g., design, web, css)",
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'image', 'tags']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tags'].initial = ', '.join([t.name for t in self.instance.tags.all()])

    def save(self, commit=True, author=None):
        post = super().save(commit=False)
        if author:
            post.author = author
        if commit:
            post.save()
            post.tags.clear()
            tags_str = self.cleaned_data.get('tags', '')
            tags_list = [t.strip() for t in tags_str.split(',') if t.strip()]
            for t_name in tags_list:
                tag_obj, _ = Tag.objects.get_or_create(name=t_name)
                post.tags.add(tag_obj)
        return post
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'نظر خود را بنویسید...'
            })
        }