from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import redirect
from sitegate.decorators import redirect_signedin, sitegate_view, signup_view

import core.models as coremodels


class LandingView(TemplateView):
    template_name = 'base/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('/location')

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class LocationListView(ListView):
    model = coremodels.Location
    template_name = 'location/list.html'
    paginate_by = 8


class LocationDetailView(DetailView):
    model = coremodels.Location
    template_name = 'location/detail.html'
    context_object_name = 'location'

    def get_context_data(self, **kwargs):
        context = super(LocationDetailView, self).get_context_data(**kwargs)

        context.update({'fb_like_url': self.request.build_absolute_uri(self.request.path)})

        return context

    def get_context_data(self, **kwargs):
        context = super(LocationDetailView, self).get_context_data(**kwargs)
        location = coremodels.Location.objects.get(id=self.kwargs['pk'])
        if self.request.user.is_authenticated():
            user_reviews = coremodels.Review.objects.filter(location=location, user=self.request.user)
            if user_reviews.count() > 0:
                context['user_review'] = user_reviews[0]
            else:
                context['user_review'] = None

        return context


class SearchListView(LocationListView):

    def get_queryset(self):
        queryset = self.model.objects.all()
        incoming_query_string = self.request.GET.get('query', '')
        incoming_area = self.request.GET.get('category', '')

        if incoming_query_string:
            queryset = queryset.filter(title__icontains=incoming_query_string)
        if incoming_area:
            queryset = queryset.filter(area=incoming_area)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(SearchListView, self).get_context_data(**kwargs)
        category = self.request.GET.get('category')
        category_val = None

        if category or category != 0:
            category_choice_dict = dict((str(x), y) for x, y in coremodels.SUBURB_CHOICES)
            category_val = category_choice_dict.get(category)

        context.update({'query': self.request.GET.get('query'),
                        'category': category_val})

        return context

class LocationCreateView(CreateView):
  model = coremodels.Location
  template_name = 'base/form.html'
  fields = "__all__"

class LocationUpdateView(UpdateView):
    model = coremodels.Location
    template_name = 'base/form.html'
    fields = "__all__"

class ReviewCreateView(CreateView):
    model = coremodels.Review
    template_name = 'base/form.html'
    fields =['description', 'rating']

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.location = coremodels.Location.objects.get(id=self.kwargs['pk'])
        return super(ReviewCreateView, self).form_valid(form)

    def get_success_url(self):
        return self.object.location.get_absolute_url()

class ReviewUpdateView(UpdateView):
    model = coremodels.Review
    template_name = 'base/form.html'
    fields =['description', 'rating']

    def get_object(self):
        return coremodels.Review.objects.get(location__id=self.kwargs['pk'], user=self.request.user)

    def get_success_url(self):
        return self.object.location.get_absolute_url()


@sitegate_view(widget_attrs={'class': 'form-control', 'placeholder': lambda f: f.label}, template='form_bootstrap3') # This also prevents logged in users from accessing our sign in/sign up page.
def entrance(request):
    return render(request, 'base/entrance.html', {'title': 'Sign in & Sign up'})