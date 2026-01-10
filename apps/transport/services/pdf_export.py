from django.template.loader import render_to_string
from weasyprint import HTML


def render_calculation_pdf(calculation, request):
    html = render_to_string(...)
    return HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()