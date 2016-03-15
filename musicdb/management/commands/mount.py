import os

from django.core.management.base import BaseCommand, CommandError
from fuse import FUSE

from ._loopback import Loopback


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('mount_point', type=str)

    def handle(self, *args, **options):
        mount_point = options['mount_point']
        if not os.path.exists(mount_point) or not os.path.isdir(mount_point):
            raise CommandError('Directory "%s" does not exists' % mount_point)
        FUSE(
                Loopback(), mount_point, foreground=True, allow_other=True
        )
        self.stdout.write(self.style.SUCCESS('Successfully mounted "%s"' % mount_point))
