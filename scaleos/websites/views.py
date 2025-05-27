from django.shortcuts import get_object_or_404
from django.shortcuts import render

from scaleos.shared.views import page_or_list_page
from scaleos.websites import models as website_models


# Create your views here.
def website(request, domain_name=None):
    context = {}

    if domain_name is None:
        websites = website_models.Website.objects.all()
        return page_or_list_page(
            request,
            website_models.Website,
            alternative_resultset=websites,
        )

    website = get_object_or_404(website_models.Website, domain_name=domain_name)
    context["website"] = website

    if website.homepage:
        return page(request, domain_name, website.homepage.slug)

    if website.pages.count() > 0:
        return page(request, domain_name, website.pages.first().slug)

    return render(request, website.page_template, context)


def page(request, domain_name, page_slug):
    context = {}

    website = get_object_or_404(website_models.Website, domain_name=domain_name)
    request.session["active_organization_id"] = website.organization.pk
    segment = request.session.get("segment", None)
    if segment is None and website.ask_segment:
        context["ask_segment"] = True

    page = get_object_or_404(website_models.Page, slug=page_slug, website_id=website.pk)
    context["page"] = page
    context["website"] = website
    return render(request, page.page_template, context)
