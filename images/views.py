from actions.utils import create_action
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.conf import settings

import redis

from .forms import ImageCreateForm
from .models import Image

# Create your views here.


r = redis.Redis(
    host = settings.REDIS_HOST,
    port = settings.REDIS_PORT,
    db = settings.REDIS_DB
)

@login_required
def image_create(request):
    if request.method == 'POST':
    # form is sent
        form = ImageCreateForm(data = request.POST)
        if form.is_valid():
            # form data is valid
            cd = form.cleaned_data
            new_image = form.save(commit = False)
            # assign current user to the item
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image)
            messages.success(request, 'Image added successfully')
            # redirect to new created item detail
            return redirect(new_image.get_absolute_url())
    else:
        # build form with data provided by the bookmarklet via GET
        form = ImageCreateForm(data = request.GET)
    return render(
        request,
        'images/image/create.html',
        {
            'section': 'images', 'form': form
        }
    )

def image_detail(request, id, slug):
    image = get_object_or_404(Image, id = id, slug = slug)
    total_views = r.incr(f'image:{image.id}:views')

    if not image.image:
        # Fallback if no image is present
        image_url = None  
    else:
        image_url = image.image.url
    user_has_liked = request.user in image.users_like.all()

    return render(
        request,
        'images/image/detail.html',
        {
            'section':'images',
            'image': image,
            'user_has_liked': user_has_liked,
            'image_url': image_url,
            'total_views': total_views
        }
    )

@require_POST
@login_required
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')

    if image_id and action:
        try:
            image = Image.objects.get(id = image_id)

            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.add(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status':'error'})


def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images_page = paginator.page(page)
    except PageNotAnInteger:
        # if page is not a integer deliver the first page
        images_page = paginator.page(1)
    except EmptyPage:
        if images_only:
            # if AJAX request and page out of range, return empty page
            return HttpResponse('')
        images_page = paginator.page(paginator.num_pages)
    print("images only",images_only)
    if images_only:
        return render(
            request,
            'images/image/list_images.html',
            {
                'section':'images',
                'images': images
            }
        )
    print("images", type(images))
    return render(
        request,
        'images/image/list.html',
        {
            'section':'images',
            "images": images
        }
    )
    