from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, 
    DeleteView, TemplateView
)
from django.views.generic.edit import FormView
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from .models import Board, Pin, Tag, Like, Privacy
from .forms import BoardForm, PinForm, TagForm


User = get_user_model()


class HomeView(TemplateView):
    """Home page view showing featured pins and boards"""
    template_name = 'core/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_pins'] = Pin.objects.filter(
            board__privacy=Privacy.PUBLIC
        ).select_related('owner', 'board').prefetch_related('tags')[:12]
        context['popular_boards'] = Board.objects.filter(
            privacy=Privacy.PUBLIC
        ).annotate(
            pin_count=Count('pins')
        ).order_by('-pin_count')[:6]
        return context


class BoardListView(ListView):
    """List all public boards or user's boards if authenticated"""
    model = Board
    template_name = 'core/board.html'
    context_object_name = 'boards'
    paginate_by = 12
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Show user's boards and public boards
            return Board.objects.filter(
                Q(owner=self.request.user) | Q(privacy=Privacy.PUBLIC)
            ).select_related('owner').prefetch_related('pins').annotate(
                pin_count=Count('pins')
            )
        else:
            return Board.objects.filter(
                privacy=Privacy.PUBLIC
            ).select_related('owner').prefetch_related('pins').annotate(
                pin_count=Count('pins')
            )


class BoardDetailView(DetailView):
    """Show board details and its pins"""
    model = Board
    template_name = 'core/board_detail.html'
    context_object_name = 'board'
    
    def get_queryset(self):
        return Board.objects.select_related('owner').prefetch_related(
            'pins__owner', 'pins__tags'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = self.get_object()
        
        # Check if user can view this board
        if board.privacy == Privacy.PRIVATE and board.owner != self.request.user:
            messages.error(self.request, "This board is private.")
            return context
        
        context['pins'] = board.pins.all()
        context['can_edit'] = self.request.user == board.owner
        return context


class BoardCreateView(LoginRequiredMixin, CreateView):
    """Create a new board"""
    model = Board
    form_class = BoardForm
    template_name = 'core/board_form.html'
    success_url = reverse_lazy('board_list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Board created successfully!')
        return super().form_valid(form)


class BoardUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing board"""
    model = Board
    form_class = BoardForm
    template_name = 'core/board_form.html'
    
    def test_func(self):
        board = self.get_object()
        return self.request.user == board.owner
    
    def get_success_url(self):
        return reverse('board_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Board updated successfully!')
        return super().form_valid(form)


class BoardDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a board"""
    model = Board
    template_name = 'core/board_confirm_delete.html'
    success_url = reverse_lazy('board_list')
    
    def test_func(self):
        board = self.get_object()
        return self.request.user == board.owner
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Board deleted successfully!')
        return super().delete(request, *args, **kwargs)


class PinListView(ListView):
    """List all public pins with search and filtering"""
    model = Pin
    template_name = 'core/pin_list.html'
    context_object_name = 'pins'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Pin.objects.filter(
            board__privacy=Privacy.PUBLIC
        ).select_related('owner', 'board').prefetch_related('tags')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()
        
        # Filter by tag
        tag_filter = self.request.GET.get('tag')
        if tag_filter:
            queryset = queryset.filter(tags__name=tag_filter)
        
        return queryset


class PinDetailView(DetailView):
    """Show pin details"""
    model = Pin
    template_name = 'core/pin_detail.html'
    context_object_name = 'pin'
    
    def get_queryset(self):
        return Pin.objects.select_related('owner', 'board').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # related pins
        context['related_pins'] = Pin.objects.filter(
            tags__in=self.object.tags.all()
        ).exclude(id=self.object.id).distinct()[:4]
        

        pin = self.get_object()
        
        # Check if user can view this pin
        if pin.board and pin.board.privacy == Privacy.PRIVATE and pin.board.owner != self.request.user:
            messages.error(self.request, "This pin is in a private board.")
            return context
        
        context['is_liked'] = False
        if self.request.user.is_authenticated:
            context['is_liked'] = pin.like_set.filter(user=self.request.user).exists()
        
        context['like_count'] = pin.like_set.count()
        context['can_edit'] = self.request.user == pin.owner
        return context


class PinCreateView(LoginRequiredMixin, CreateView):
    """Create a new pin"""
    model = Pin
    form_class = PinForm
    template_name = 'core/pin_form.html'
    
    def get_success_url(self):
        return reverse('pin_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Pin created successfully!')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class PinUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing pin"""
    model = Pin
    form_class = PinForm
    template_name = 'core/pin_form.html'
    
    def test_func(self):
        pin = self.get_object()
        return self.request.user == pin.owner
    
    def get_success_url(self):
        return reverse('pin_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Pin updated successfully!')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class PinDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a pin"""
    model = Pin
    template_name = 'core/pin_confirm_delete.html'
    
    def test_func(self):
        pin = self.get_object()
        return self.request.user == pin.owner
    
    def get_success_url(self):
        board = self.object.board
        if board:
            return reverse('board_detail', kwargs={'pk': board.pk})
        return reverse('pin_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Pin deleted successfully!')
        return super().delete(request, *args, **kwargs)


class UserProfileView(DetailView):
    """Show user profile with their boards and pins"""
    model = User
    template_name = 'core/user_profile.html'
    context_object_name = 'profile_user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        # Get user's public boards
        context['boards'] = Board.objects.filter(
            owner=user, privacy=Privacy.PUBLIC
        ).prefetch_related('pins').annotate(pin_count=Count('pins'))
        
        # Get user's public pins
        context['pins'] = Pin.objects.filter(
            owner=user, board__privacy=Privacy.PUBLIC
        ).select_related('board').prefetch_related('tags')

        profile_user = self.get_object()
        context['profile_user'] = profile_user
        # Check if viewing own profile
        context['is_own_profile'] = self.request.user == user
        return context


class TagListView(ListView):
    """List all tags with pin counts"""
    model = Tag
    template_name = 'core/tag_list.html'
    context_object_name = 'tags'
    
    def get_queryset(self):
        return Tag.objects.annotate(
            pin_count=Count('pins', filter=Q(pins__board__privacy=Privacy.PUBLIC))
        ).filter(pin_count__gt=0).order_by('-pin_count')


class TagDetailView(DetailView):
    """Show pins for a specific tag"""
    model = Tag
    template_name = 'core/tag_detail.html'
    context_object_name = 'tag'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = self.get_object()
        context['pins'] = tag.pins.filter(
            board__privacy=Privacy.PUBLIC
        ).select_related('owner', 'board').prefetch_related('tags')
        return context


# API-like views for AJAX functionality
@login_required
@require_POST
def toggle_like(request, pin_id):
    """Toggle like/unlike a pin"""
    pin = get_object_or_404(Pin, id=pin_id)
    like, created = Like.objects.get_or_create(user=request.user, pin=pin)
    
    if not created:
        # Unlike
        like.delete()
        liked = False
    else:
        # Like
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'like_count': pin.like_set.count()
    })


@login_required
@require_POST
def save_pin_to_board(request, pin_id):
    """Save a pin to a board"""
    pin = get_object_or_404(Pin, id=pin_id)
    board_id = request.POST.get('board_id')
    
    if board_id:
        board = get_object_or_404(Board, id=board_id, owner=request.user)
        pin.board = board
        pin.save()
        messages.success(request, f'Pin saved to "{board.title}"!')
    else:
        messages.error(request, 'Please select a board.')
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('pin_list')))


class SearchView(ListView):
    """Search pins, boards, and users"""
    model = Pin
    template_name = 'core/search.html'
    context_object_name = 'pins'
    paginate_by = 20
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if not query:
            return Pin.objects.none()
        
        return Pin.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query),
            board__privacy=Privacy.PUBLIC
        ).select_related('owner', 'board').prefetch_related('tags').distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        
        if query:
            # Search boards
            context['boards'] = Board.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query),
                privacy=Privacy.PUBLIC
            ).select_related('owner')[:5]
            
            # Search users
            context['users'] = User.objects.filter(
                username__icontains=query
            )[:5]
        
        context['query'] = query
        return context
