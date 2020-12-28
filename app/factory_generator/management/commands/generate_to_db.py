from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction, DEFAULT_DB_ALIAS

from factory_generator.generators import generate_to_db


class Command(BaseCommand):
    help = 'Fill database using data generated by factories in django apps'

    def add_arguments(self, parser):
        parser.add_argument(
            'args', metavar='app_label[.FactoryName]', nargs='*',
            help='Restricts dumped data to the specified app_label or app_label.ModelName.',
        )

        parser.add_argument(
            '--database',
            default=DEFAULT_DB_ALIAS,
            help='Nominates a specific database to dump fixtures from. '
                 'Defaults to the "default" database.',
        )

        parser.add_argument(
            '-e', '--exclude', action='append', default=[],
            help='An app_label or app_label.FactoryName to exclude '
                 '(use multiple --exclude to exclude multiple apps/factories).',
        )

        parser.add_argument(
            '-q', '--quantity', type=int, default=1, nargs='?',
            help='Quantity of inctances of each models which will be generate to database',
        )

        parser.add_argument(
            '-u', '--update', action='store_true',
            help='If specified, database will be rewrite. If not, new records will be added.',
        )

    def handle(self, *args, **options):
        database = options['database']
        excludes = options['exclude']

        import pdb; pdb.set_trace()