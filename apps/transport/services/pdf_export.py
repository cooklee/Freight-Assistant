from django.template.loader import render_to_string
from weasyprint import HTML

#todo to jest nie używane wiec po to to to i jeszcze
def render_calculation_pdf(calculation, request):
    html = render_to_string(...)
    #todo to tez nie zadziała z ellipsis
    return HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
