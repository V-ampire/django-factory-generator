from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from factory_generator.management.base import BaseGenerateCommand
from factory_generator.management.commands.generate_to_db import GenerateToDbCommand
from factory_generator.utils import Config, get_full_file_path

from sample_app.factories import CityFactory
from sample_app.models import City

from faker import Faker
from io import StringIO
from unittest.mock import patch, call, Mock


fake = Faker()


class TestBaseGenerateCmd(TestCase):

    def setUp(self):
        self.cmd = BaseGenerateCommand()

    @patch('factory_generator.management.base.BaseGenerateCommand.handle')
    def test_default_options(self, mock_handle):
        mock_handle.return_value = ''
        expected_exclude = []
        expected_update = False
        expected_quantity = 1
        expected_file = None
        call_command(self.cmd)
        tested_call_kwargs = mock_handle.call_args.kwargs

        self.assertEqual(tested_call_kwargs['exclude'], expected_exclude)
        self.assertEqual(tested_call_kwargs['update'], expected_update)
        self.assertEqual(tested_call_kwargs['quantity'], expected_quantity)
        self.assertEqual(tested_call_kwargs['file'], expected_file)

    @patch('factory_generator.management.base.BaseGenerateCommand.generate')
    @patch('factory_generator.management.base.utils.load_file_config')
    def test_load_options_from_file(self, mock_load_config, mock_generate):
        expected_exclude = []
        expected_update = True
        expected_quantity = 3
        expected_labels = []
        expected_file = fake.file_name(extension='ini')
        expected_config = Config(labels=expected_labels, exclude=expected_exclude, 
                                    update=expected_update, quantity=expected_quantity)
        mock_load_config.return_value = expected_config
        call_command(self.cmd, file=expected_file)

        mock_load_config.assert_called_with(get_full_file_path(expected_file))
        mock_load_config.assert_called_once()

    @patch('factory_generator.management.base.utils.load_file_config')
    def test_raise_file_not_found(self, mock_load_config):
        file_path = fake.file_name(extension='ini')
        expected_message = f'Configuration file {get_full_file_path(file_path)} not found.'
        mock_load_config.side_effect = FileNotFoundError
        with self.assertRaises(CommandError) as e:
            exc = e
            call_command(self.cmd, file=file_path)
        tested_message = exc.exception.args[0]

        self.assertEqual(expected_message, tested_message)


    @patch('factory_generator.management.base.BaseGenerateCommand.handle')
    @patch('factory_generator.management.base.utils.parse_apps_and_factories_labels')
    def test_with_labels_option(self, mock_parse, mock_handle):
        mock_handle.return_value = ''
        mock_parse.return_value = []
        expected_labels = ('some_app', 'sample_app.Person')
        call_command(self.cmd, *expected_labels)

        self.assertEqual(mock_handle.call_args.args, expected_labels)
        mock_handle.assert_called_once()


    @patch('factory_generator.management.base.BaseGenerateCommand.handle')
    @patch('factory_generator.management.base.utils.parse_apps_and_factories_labels')
    def test_with_exclude_option(self, mock_parse, mock_handle):
        mock_handle.return_value = ''
        mock_parse.return_value = []
        expected_excludes = ['some_app', 'sample_app.Person']
        call_command(self.cmd, exclude=expected_excludes)

        self.assertEqual(mock_handle.call_args.kwargs['exclude'], expected_excludes)
        mock_handle.assert_called_once()


    @patch('factory_generator.management.base.installed_apps.get_app_configs')
    @patch('factory_generator.management.base.utils.get_app_factories')
    @patch('factory_generator.management.base.BaseGenerateCommand.generate')
    def test_call_generate_without_labels(self, mock_generate, mock_factories, mock_apps):
        app_config = Mock()
        generate_factories = [Mock(), Mock()]
        mock_apps.return_value = [app_config]
        mock_factories.return_value = generate_factories
        call_command(self.cmd)

        self.assertEqual(mock_generate.call_args.args[0], generate_factories)
        mock_generate.assert_called_once()


    @patch('factory_generator.management.base.utils.parse_apps_and_factories_labels')
    @patch('factory_generator.management.base.BaseGenerateCommand.generate')
    def test_call_generate_with_labels(self, mock_generate, mock_factories):
        expected_labels = ('sample_app', 'sample_app.City')
        generate_factories = [Mock(), Mock()]
        mock_factories.return_value = generate_factories
        call_command(self.cmd, *expected_labels)

        self.assertEqual(mock_generate.call_args.args[0], generate_factories)
        mock_generate.assert_called_once()
        mock_factories.assert_called_with(expected_labels)


    @patch('factory_generator.management.base.utils.exclude_factories')
    @patch('factory_generator.management.base.utils.parse_apps_and_factories_labels')
    @patch('factory_generator.management.base.BaseGenerateCommand.generate')
    def test_call_generate_with_excludes(self, mock_generate, mock_factories, mock_excludes):
        labels = ('sample_app', 'sample_app.City')
        exclude_factories_list = [Mock(), Mock()]
        generate_factories = [Mock(), Mock()]
        mock_factories.side_effect = [generate_factories, exclude_factories_list]
        expected_factories = [Mock()]
        mock_excludes.return_value = expected_factories
        call_command(self.cmd, *labels, exclude=labels)

        mock_generate.assert_called_once()
        self.assertEqual(mock_generate.call_args.args[0], expected_factories)
        mock_excludes.assert_called_with(generate_factories, exclude_factories_list)


    @patch('factory_generator.management.base.utils.parse_apps_and_factories_labels')
    @patch('factory_generator.management.base.BaseGenerateCommand.generate')
    def test_call_generate_with_quantity(self, mock_generate, mock_factories):
        labels = ('sample_app', 'sample_app.City')
        expected_quantity = fake.pyint()
        call_command(self.cmd, *labels, quantity=expected_quantity)
        
        self.assertEqual(mock_generate.call_args.kwargs['quantity'], expected_quantity)


    @patch('factory_generator.management.base.utils.parse_apps_and_factories_labels')
    @patch('factory_generator.management.base.BaseGenerateCommand.generate')
    def test_call_generate_with_update(self, mock_generate, mock_factories):
        labels = ('sample_app', 'sample_app.City')
        expected_update = True
        call_command(self.cmd, *labels, update=expected_update)
        
        self.assertEqual(mock_generate.call_args.kwargs['update'], expected_update)


class TestGenerateToDbCmd(TestCase):

    def setUp(self):
        self.cmd = GenerateToDbCommand()

    @patch('factory_generator.management.commands.generate_to_db.generate_to_db')
    def test_generate(self, mock_generate):
        expected_factory = CityFactory
        factories = [expected_factory]
        self.cmd.generate(factories)
        mock_generate.assert_called_once()
        mock_generate.assert_called_with(expected_factory, quantity=1)

    @patch('factory_generator.management.commands.generate_to_db.generate_to_db')
    @patch('factory_generator.management.commands.generate_to_db.utils.delete_by_factory')
    def test_generate_with_update(self, mock_delete, mock_generate):
        expected_factory = CityFactory
        factories = [expected_factory]
        mock_delete.return_value = (1, {})
        self.cmd.generate(factories, update=True)
        mock_delete.assert_called_once()
        mock_delete.assert_called_with(expected_factory)
        mock_generate.assert_called_once()
        mock_generate.assert_called_with(expected_factory, quantity=1)

    @patch('factory_generator.management.commands.generate_to_db.generate_to_db')
    def test_generate_with_quantity(self, mock_generate):
        expected_factory = CityFactory
        expected_quantity = fake.pyint()
        factories = [expected_factory]
        self.cmd.generate(factories, quantity=expected_quantity)
        mock_generate.assert_called_once()
        mock_generate.assert_called_with(expected_factory, quantity=expected_quantity)

    @patch('factory_generator.management.commands.generate_to_db.generate_to_db')
    def test_atomic(self, mock_generate):
        expected_city = CityFactory.create()
        factories = [CityFactory]
        mock_generate.side_effect = Exception()
        with self.assertRaises(Exception):
            self.cmd.generate(factories, update=True)
        self.assertTrue(City.objects.filter(pk=expected_city.pk).exists())

