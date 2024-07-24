from os import path

from core import views


urlpatterns = [
    # a path to the images/{yr}/{mo}/{day} directory
    path("images/<int:year>/<int:month>/<int:day>/", views.images),
]
