def view_name(request):
    try:
        return {"view_name": request.resolver_match.url_name}
    except AttributeError:
        return ""

    return ""
