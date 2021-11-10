from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from estore import views as v1

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('estore.urls')),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='estore/a.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="estore/b.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='estore/c.html'), name='password_reset_complete'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)