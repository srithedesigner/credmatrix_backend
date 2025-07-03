from django.urls import path
from .views.auth_views import signup_view, login_view, logout_view, send_otp_view
from .views.user_views import (
    GetReportsView,
    EditReportView,
    DeleteReportView,
    InitiateRequestView,
    UploadDocumentView,
    ConfirmDocumentUploadView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('signup/', signup_view.as_view(), name='signup'),
    path('login/', login_view.as_view(), name='login'),
    path('logout/', logout_view.as_view(), name='logout'),
    path('send_otp/', send_otp_view.as_view(), name='otp'),
    
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

]




urlpatterns += [
    path('reports/', GetReportsView.as_view(), name='get-reports'),
    path('reports/<int:report_id>/edit/', EditReportView.as_view(), name='edit-report'),
    path('reports/<int:report_id>/delete/', DeleteReportView.as_view(), name='delete-report'),
    path('reports/initiate/', InitiateRequestView.as_view(), name='initiate-request'),

    path('documents/upload/', UploadDocumentView.as_view(), name='upload-document'),
    path('documents/confirm/', ConfirmDocumentUploadView.as_view(), name='confirm-document-upload'),
]