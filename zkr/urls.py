"""zkr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.defaults import page_not_found
from django.views.generic import RedirectView

from zkr import settings
from zkr.sitemap import StaticViewSitemap, SeimasPoliticianSitemap

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('seimas/', include('seimas.urls')),
                  path('Rinkimai-2019/', include('elections.urls')),
                  path('klausimai/', include('questions.urls')),
                  path('api/', include('api.urls')),
                  path(
                      'sitemap.xml/',
                      sitemap,
                      {'sitemaps': {'static': StaticViewSitemap, 'seimas': SeimasPoliticianSitemap}},
                      name='django.contrib.sitemaps.views.sitemap'
                  ),
                  path('', include('web.urls')),

                  # Disable changing e-mail
                  path("accounts/email/", page_not_found, name="account_email"),
                  path('accounts/social/connections/',
                       RedirectView.as_view(pattern_name="user_profile", permanent=False)),

                  path('accounts/', include('allauth.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
