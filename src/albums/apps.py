from django.apps import AppConfig
from django.db.models.signals import post_migrate

# def do_stuff(sender, **kwargs):
#     mymodel = sender.get_model('Album')
#     mymodel.objects.get() # etc...


class AlbumsConfig(AppConfig):
    name = 'albums'

    # def ready(self):
    #     post_migrate.connect(do_stuff, sender=self)