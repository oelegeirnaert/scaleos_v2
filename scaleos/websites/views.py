from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse


from scaleos.shared.views import page_or_list_page
from scaleos.websites import models as website_models


# Create your views here.
def website(request):
    context = {}

    website = request.website

    if website:
        if website.homepage:
            return page(request, website.homepage.slug)

        if website.pages.count() > 0:
            return page(request, website.pages.first().slug)

        return render(request, website.page_template, context)
    
    return redirect(reverse('home'))


def page(request, page_slug):
    context = {}

    website = request.website
    request.session["active_organization_id"] = website.organization.pk
    segment = request.session.get("segment", None)
    if segment is None and website.ask_segment:
        context["ask_segment"] = True

    page = get_object_or_404(website_models.Page, slug=page_slug, website_id=website.pk)
    context["page"] = page

    return render(request, page.page_template, context)
