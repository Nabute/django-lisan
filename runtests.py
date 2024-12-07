import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
import coverage

if __name__ == '__main__':
    # Initialize coverage and start it
    cov = coverage.Coverage(source=[])
    cov.start()

    # Set up Django environment
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    # Run tests
    failures = test_runner.run_tests(['tests'])

    # Stop coverage and save report
    cov.stop()
    cov.save()

    # Generate coverage report
    print("\nCoverage Report:")
    cov.report(show_missing=True)

    # Exit with appropriate status code
    sys.exit(bool(failures))
