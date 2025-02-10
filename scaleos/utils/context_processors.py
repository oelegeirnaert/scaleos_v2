def view_name(request):
    return {"view_name": request.resolver_match.url_name}
