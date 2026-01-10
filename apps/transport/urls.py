from django.urls import path

# CALCULATION views
from .views import (
    CalculationListView,
    CalculationDetailView,
    CalculationCreateView,
    CalculationUpdateView,
    CalculationDeleteView,
    CalculationPdfView
)
# ROUTE views
from .views import (
    RouteListView,
    RouteDetailView,
    RouteCreateView,
    RouteUpdateView,
    RouteDeleteView,
    RouteWithStopsCreateView,
)
# STOP views
from .views import (

    StopCreateView,
    StopUpdateView,
    StopDeleteView,
)
# DYNAMIC FILTER
from .views import drivers_by_carrier
# TRANSPORT ORDER views
from .views.transport_order import (
    TransportOrderListView,
    TransportOrderDetailView,
    TransportOrderCreateView,
    TransportOrderUpdateView,
    TransportOrderDeleteView,
)

urlpatterns = [
    # DYNAMIC FILTER
    path("ajax/drivers/<int:carrier_id>/", drivers_by_carrier, name="drivers-by-carrier"),

    # ROUTES
    path("routes/", RouteListView.as_view(), name="route-list"),
    path("routes/<int:route_id>/", RouteDetailView.as_view(), name="route-detail"),
    path("routes/add/", RouteCreateView.as_view(), name="route-create"),
    path("routes/<int:route_id>/update/", RouteUpdateView.as_view(), name="route-update"),
    path("routes/<int:route_id>/delete/", RouteDeleteView.as_view(), name="route-delete"),

    # Special View: Route + Inline Stops Formset
    path("routes/add-with-stops/", RouteWithStopsCreateView.as_view(), name="route-with-stops"),

    # STOPS
    path("routes/<int:route_id>/stops/add/", StopCreateView.as_view(), name="stop-add"),
    path("stops/<int:stop_id>/update/", StopUpdateView.as_view(), name="stop-update"),
    path("stops/<int:stop_id>/delete/", StopDeleteView.as_view(), name="stop-delete"),

    # CALCULATIONS
    path("calculations/", CalculationListView.as_view(), name="calculation-list"),
    path("calculations/<int:calculation_id>/", CalculationDetailView.as_view(), name="calculation-detail"),
    path("calculations/add/", CalculationCreateView.as_view(), name="calculation-create"),
    path("calculations/<int:calculation_id>/update/", CalculationUpdateView.as_view(), name="calculation-update"),
    path("calculations/<int:calculation_id>/delete/", CalculationDeleteView.as_view(), name="calculation-delete"),
    path("calculations/<int:calculation_id>/pdf/", CalculationPdfView.as_view(), name="calculation-pdf"),

    # TRANSPORT ORDERS
    path("orders/", TransportOrderListView.as_view(), name="order-list"),
    path("orders/add/", TransportOrderCreateView.as_view(), name="order-create"),
    path("orders/<int:order_id>/", TransportOrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:order_id>/update/", TransportOrderUpdateView.as_view(), name="order-update"),
    path("orders/<int:order_id>/delete/", TransportOrderDeleteView.as_view(), name="order-delete"),
]
