import os

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from .models import *
from .forms import *

FORBIDDEN_WORDS = str(os.getenv('FORBIDDEN_WORDS'))


# DUMPLINGS VIEWS

class ListDumplings(ListView):
    model = Dumpling
    template_name = 'dumpling/list_view.html'
    context_object_name = 'dumplings'

    def get_queryset(self):     # Какие данные выбирать из бд
        if self.request.GET:
            try:
                for k, v in self.request.GET.items():
                    quest = {k: int(v)}
                    return Dumpling.objects.filter(**quest)
            except:
                messages.error(self.request, 'Wrong URL', extra_tags='alert-danger')
        else:
            return Dumpling.objects.all()


class IndexDumpling(DetailView):
    model = Dumpling
    template_name = 'dumpling/index.html'
    context_object_name = 'dumpling'
    slug_url_kwarg = 'dumpling_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Пельмень'
        slug = self.kwargs['dumpling_slug']

        form = DumplingAddCommentForm()
        post = get_object_or_404(Dumpling, slug=slug)
        comments = post.dumpling_comments.filter(is_published=True)
        paginate = Paginator(comments, per_page=5)
        page_get = self.request.GET.copy()
        if 'page' not in page_get:
            page_get['page'] = 1
        page_obj = paginate.get_page(page_get['page'])

        context['post'] = post
        context['comments'] = comments
        context['page_range'] = list(paginate.get_elided_page_range(int(page_get['page']), on_each_side=1, on_ends=1))
        context['page_obj'] = page_obj
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        form = DumplingAddCommentForm(request.POST)
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)

        post = Dumpling.objects.filter(slug=self.kwargs['dumpling_slug'])[0]
        comments = post.dumpling_comments.filter(is_published=True)

        context['post'] = post
        context['comments'] = comments
        context['form'] = form

        if form.is_valid():
            comment = form.cleaned_data['comment']
            dumpling = post
            author = self.request.user

            check_words = [word.lower().strip('/?.,!+-=_ ') for word in comment.split()]
            if any([word in FORBIDDEN_WORDS for word in check_words]):
                self.request.user.profile.up_chort_status()
                self.request.user.profile.save()
                created_comment = DumplingComment.objects.create(comment=comment,
                                                                 dumpling=dumpling,
                                                                 author=author,
                                                                 is_published=False,
                                                                 bad_status=True)
            else:
                created_comment = DumplingComment.objects.create(comment=comment, dumpling=dumpling, author=author)

            form = DumplingAddCommentForm()
            context['form'] = form
            messages.success(request, 'Thank you for your feedback, your opinion is very important to us, honestly',
                             extra_tags='alert-success')
            # Always return an HttpResponseRedirect after successfully dealing with POST data.
            # This prevents data from being posted twice if a user hits the Back button.
            return HttpResponseRedirect(reverse('dumpling-detail-view',
                                                kwargs={'dumpling_slug': self.kwargs['dumpling_slug']}))

        return self.render_to_response(context=context)


# USER VIEWS

class DumplingAddPost(PermissionRequiredMixin, CreateView):
    form_class = DumplingAddPostForm
    success_url = reverse_lazy('home')
    permission_required = 'is_superuser'
    raise_exception = True
    template_name = 'dumpling/addpost.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление статьи'
        return context


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/registration.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context

    def form_valid(self, form):
        user = form.save()
        user.refresh_from_db()
        user.profile.username = form.cleaned_data.get('username')
        user.profile.first_name = form.cleaned_data.get('first_name')
        user.profile.last_name = form.cleaned_data.get('last_name')
        user.profile.email = form.cleaned_data.get('email')
        user.profile.credit_card_number = form.cleaned_data.get('credit_card_number')
        user.profile.cvc_code = form.cleaned_data.get('cvc_code')
        user.profile.address = form.cleaned_data.get('address')
        user.profile.where_key = form.cleaned_data.get('where_key')
        user.profile.passport_number = form.cleaned_data.get('passport_number')
        user.profile.bio = form.cleaned_data.get('bio')
        user.profile.slug = form.cleaned_data.get('slug')

        user.save()

        # login after registration
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')

    # To prevent access authorized users to the register page, need override the 'dispatch' method.
    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='home')

        # else process dispatch as it otherwise normally would
        return super(RegisterUser, self).dispatch(request, *args, **kwargs)


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:     # куки данных для авторизации, не уверен в работоспособности, нужно проверить
                                # UPD: Проверил, не работает

            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(LoginUser, self).form_valid(form)


def logout_user(request):
    logout(request)
    return redirect('home')


class ResetUserPassword(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'

    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."

    # If not given any, django defaults to 'password_reset_done' after a successful password request
    success_url = reverse_lazy('login')


@login_required
def profile(request, profile_slug):
    if profile_slug == request.user.profile.slug:
        if request.method == 'POST':
            user_form = UpdateUserForm(request.POST, instance=request.user)
            profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

            if user_form.is_valid():
                if profile_form.is_valid():
                    user_form.save()
                    profile_form.save()
                    return redirect(to='user_profile', profile_slug=request.POST['slug'])
            else:
                messages.error(request, 'profile form NOT valid', extra_tags='alert-danger')
        else:
            user_form = UpdateUserForm(instance=request.user)
            profile_form = UpdateProfileForm(instance=request.user.profile)

        comments = DumplingComment.objects.filter(author=request.user)

        paginate = Paginator(comments, per_page=5)
        page_get = request.GET.copy()
        if 'page' not in page_get:
            page_get['page'] = 1
        page_obj = paginate.get_page(page_get['page'])
        page_obj.adjusted_elided_pages = paginate.get_elided_page_range(page_get['page'])
        page_range = list(paginate.get_elided_page_range(int(page_get['page']), on_each_side=1, on_ends=1))

        return render(request, 'users/my_profile.html', {'user_form': user_form,
                                                         'profile_form': profile_form,
                                                         'comments': comments,
                                                         'page_obj': page_obj,
                                                         'page_range': page_range})
    else:
        messages.error(request, 'Page Not found', extra_tags='alert-danger')
        return redirect(to='home')


# COMMENTS VIEWS

def dumpling_comment_like(request, pk):
    comment = get_object_or_404(DumplingComment, id=pk)
    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)

    if request.GET['next']:
        return redirect(to=request.GET['next'])
    else:
        return reverse('home')


def dumpling_comment_delete(request, pk):
    comment = get_object_or_404(DumplingComment, id=pk)
    comment.delete()

    if request.GET['next']:
        return redirect(to=request.GET['next'])
    else:
        return reverse('home')


def dumpling_comment_ban(request, pk):
    comment = get_object_or_404(DumplingComment, id=pk)

    comment.author.profile.up_chort_status()
    comment.author.profile.save()

    comment.delete()

    if request.GET['next']:
        return redirect(to=request.GET['next'])
    else:
        return reverse('home')


class DumplingCommentUpdateView(UpdateView):
    model = DumplingComment
    form_class = DumplingAddCommentForm
    template_name = 'dumpling/comment_update.html'
    pk_url_kwarg = 'pk'
    success_url = '/dumpling/black'

    def form_valid(self, form):
        comment = form.save(commit=False)

        check_comment = comment.comment
        check_words = [word.lower().strip('/?.,!+-=_ ') for word in check_comment.split()]
        if any([word in FORBIDDEN_WORDS for word in check_words]):
            self.request.user.profile.up_chort_status()
            self.request.user.profile.save()
            comment.is_published = False
            comment.bad_status = True

        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        # According to the documentation, get_success_url should just return the URL to redirect to,
        # not the redirect response (not redirect(...))
        return self.request.GET.get('next', reverse('home'))


def home_view(request):
    return redirect('dumpling/black')


def about(request):
    return render(request, 'dumpling/about.html')
