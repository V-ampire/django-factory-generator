from django.db import transaction

from factory_generator.generators import generate_to_db
from factory_generator import utils
from factory_generator.management.base import BaseGenerateCommand


class GenerateToDbCommand(BaseGenerateCommand):
    help = 'Fill database using data generated by factories in django apps'

    def generate(self, generate_factories, update=False, quantity=1):
        with transaction.atomic():
            if update:
                for factory_class in generate_factories:
                    result = utils.delete_by_factory(factory_class)
                    deleted_count = result[0]
                    if deleted_count > 0:
                        deleted_models = [str(m) for m in result[1].keys()]
                        message = f"Deleted {result[0]} record(s) of {','.join(deleted_models)}"
                        self.stdout.write(self.style.SUCCESS(message))

            for factory_class in generate_factories:
                generate_to_db(factory_class, quantity=quantity)
                message = f'Successfully created {quantity} objects of model {factory_class._meta.model}'
                self.stdout.write(self.style.SUCCESS(message))
        
