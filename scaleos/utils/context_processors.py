def body_classes(request):
    return {
        "app_name": request.resolver_match.app_name,
        "view_name": request.resolver_match.url_name,
    }


def hideable_page_parts(request):
    show_header = True
    try:
        request.GET["hide-header"]
        show_header = False
    except KeyError:
        pass

    show_footer = True
    try:
        request.GET["hide-footer"]
        show_footer = False
    except KeyError:
        pass

    return {
        "show_header": show_header,
        "show_footer": show_footer,
    }
