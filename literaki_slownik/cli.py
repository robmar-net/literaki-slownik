"""Polskie polecenia operatora; jedna odpowiedź JSON na stdout."""
import argparse
import sys
from .canonical import dumps
from .inputs import GeneratorError, inspect_sources


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise GeneratorError('Błąd argumentów: ' + message, 2)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    command = argv[0] if argv else None
    result = {'schema_version': 1, 'command': command, 'status': 'ok', 'diagnostics': []}
    try:
        parser = Parser(description='Generator słowników Literaki Lounge')
        sub = parser.add_subparsers(dest='command', required=True, parser_class=Parser)
        inspect = sub.add_parser('inspect-sources', help='Sprawdź jawne źródła i ich SHA256')
        inspect.add_argument('--manifest', required=True, help='Manifest lokalnych wejść')
        inspect.add_argument('--json', action='store_true', help='Odpowiedź JSON')
        builder = sub.add_parser('build', help='Zbuduj nowy przebieg')
        builder.add_argument('--manifest', required=True, help='Manifest lokalnych wejść')
        builder.add_argument('--run-dir', required=True, help='Nowy katalog przebiegu')
        builder.add_argument('--json', action='store_true', help='Odpowiedź JSON')
        explainer = sub.add_parser('explain', help='Wyjaśnij źródłowe analizy i niewiadome (diagnostyka)')
        explainer.add_argument('--run-dir', required=True, help='Katalog przebiegu do odczytu')
        explainer.add_argument('--word', required=True, help='Słowo do wyszukania przez NFC/lower')
        explainer.add_argument('--variant', choices=('broad', 'standard'), default='standard', help='Wariant słownika')
        explainer.add_argument('--json', action='store_true', help='Wszystkie analizy w JSON')
        args = parser.parse_args(argv)
        if args.command == 'inspect-sources':
            checked = inspect_sources(args.manifest)
            result['result'] = {k: v for k, v in checked.items() if k != 'manifest'}
        elif args.command == 'build':
            from .build import build
            result['result'] = build(args.manifest, args.run_dir)
        elif args.command == 'explain':
            from .explain import explain
            result['result'] = explain(args.run_dir, args.word, args.variant)
        code = 0
    except GeneratorError as error:
        result.update(status='error', diagnostics=[error.diagnostic()])
        print(str(error), file=sys.stderr)
        code = error.code
    except KeyboardInterrupt:
        result.update(status='error', diagnostics=[{'code': 130, 'message': 'Przerwano operację'}])
        code = 130
    except OSError as error:
        result.update(status='error', diagnostics=[{'code': 4, 'message': str(error)}])
        print(str(error), file=sys.stderr)
        code = 4
    if '--json' in argv:
        print(dumps(result))
    elif result['status'] == 'ok':
        if command == 'explain':
            from .explain import format_explanation
            print(format_explanation(result['result']))
        else:
            print('Kontrola zakończona: ' + dumps(result.get('result', {})))
    return code
