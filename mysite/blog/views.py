from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import CommentForm
from django.views.decorators.http import require_POST
from taggit.models import Tag


# class PostListView(ListView):
#     """
#     Classed based view for listing posts
#     """
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 7
#     template_name = 'blog/post/list.html'


def post_list(request, tag_slug=None):
    all_posts = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        all_posts = all_posts.filter(tags__in=[tag])

    # pagination with 7 posts per page
    paginator = Paginator(all_posts, 7)
    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)  # displays last page
    except PageNotAnInteger:
        posts = paginator.page(1)  # displays first page
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day,
                             slug=post)
    # list of active comments for this post
    comments = post.comments.filter(active=True)
    # comment form for users
    form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'form': form})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # create a Comment object without saving to the database
        comment = form.save(commit=False)
        # assign the post to the comment
        comment.post = post
        # save the comment to the database
        comment.save()

    return render(request, 'blog/post/comment.html', {'post': post,
                                                      'form': form,
                                                      'comment': comment})
