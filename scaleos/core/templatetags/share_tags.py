from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def share_button(context, link=None):
    if link is None:
        return ""
    request = context["request"]
    share_link = (
        request.build_absolute_uri(link) if link else request.build_absolute_uri()
    )

    html = f"""
    <div class="relative inline-block">
        <button id="shareBtn" data-link="{share_link}"
            class="cursor-pointer inline-flex items-center px-4 py-3
            bg-gray-600 text-white text-sm font-medium rounded-md
            hover:bg-gray-700 focus:outline-none focus:ring-2
            focus:ring-offset-2 focus:ring-gray-500 transition">
            <i data-lucide="share-2" class="w-5 h-5"></i>
        </button>
        <span id="copiedMsg"
              class="absolute left-full ml-3 top-1/2 -translate-y-1/2
              text-green-600 text-sm font-medium hidden">
              Copied!
        </span>
    </div>

    <script>
        (function () {{
            function initShareButton(el) {{
                const btn = el.querySelector('#shareBtn');
                const msg = el.querySelector('#copiedMsg');
                if (btn && msg) {{
                    btn.addEventListener('click', () => {{
                        const link = btn.getAttribute('data-link');
                        navigator.clipboard.writeText(link).then(() => {{
                            msg.classList.remove('hidden');
                            setTimeout(() => msg.classList.add('hidden'), 2000);
                        }});
                    }});
                }}
                if (typeof lucide !== 'undefined') {{
                lucide.createIcons({{ icons: el.querySelectorAll('[data-lucide]') }});
                }}
            }}

            const wrapper = document.currentScript.closest('div');

            if (window.htmx) {{
                htmx.onLoad(initShareButton);
            }} else {{
                initShareButton(wrapper);
            }}
        }})();
    </script>
    """
    return mark_safe(html)  # noqa: S308
