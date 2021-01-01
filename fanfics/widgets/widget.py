from django import forms


class SelectCustomWidget(forms.widgets.Select):
    class Media:
        css = {
            'all': ("css/admin.css", "css/external/toastr.min.css",
                    "css/external/selectize.css",)
        }
        js = ("js/external/jquery-3.3.1.min.js", "js/external/toastr.min.js",
              "js/external/selectize.js",
              "js/admin.js")
