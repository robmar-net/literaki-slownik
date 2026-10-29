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
        explainer.add_argument('--variant', choices=('broad', 'standard', 'pop', 'pop0', 'pop00'), default='standard',
                               help='Wariant słownika; pop i pop0 wymagają --pop-dir')
        explainer.add_argument('--pop-dir', help='Pakiet POP (wymagany przy --variant pop|pop0)')
        explainer.add_argument('--pop00-dir', help='Pakiet POP00 (wymagany przy --variant pop00)')
        explainer.add_argument('--json', action='store_true', help='Wszystkie analizy w JSON')
        verifier = sub.add_parser('verify', help='Odbiór K1–K10 z drugim build i przeglądem')
        verifier.add_argument('--run-dir', required=True, help='Przebieg do odbioru')
        verifier.add_argument('--peer-run', required=True, help='Niezależny drugi przebieg z tych samych wejść')
        verifier.add_argument('--review', required=True, help='Przegląd quality-v1 związany hashami')
        verifier.add_argument('--json', action='store_true', help='Odpowiedź JSON')
        exporter = sub.add_parser('export', help='Zamroź zweryfikowany pakiet w nowym katalogu')
        exporter.add_argument('--run-dir', required=True, help='Przebieg VERIFIED')
        exporter.add_argument('--output-dir', required=True, help='Nowy, nieistniejący katalog pakietu')
        exporter.add_argument('--json', action='store_true', help='Odpowiedź JSON')
        popper = sub.add_parser('pop', help='Listy POP i POP0 metodą z pop.json (pop-v3: ADR-008; pop-v2: ADR-007)')
        popper.add_argument('--manifest', required=True, help='Manifest źródeł POP (pop-sources.json)')
        popper.add_argument('--config', required=True, help='Konfiguracja metody (pop.json)')
        popper.add_argument('--run-dir', help='Przebieg FROZEN; domyślnie z manifestu')
        popper.add_argument('--release-dir', help='Pakiet LL-PL; domyślnie z manifestu')
        popper.add_argument('--output-dir', required=True, help='Nowy, nieistniejący katalog pakietu POP')
        popper.add_argument('--json', action='store_true', help='Odpowiedź JSON')
        pop00 = sub.add_parser('pop00', help='Zbuduj POP00 z zamrożonego POP0 (ADR-009)')
        pop00.add_argument('--manifest', required=True, help='Manifest przypiętych wejść POP00')
        pop00.add_argument('--config', required=True, help='Zatwierdzona konfiguracja POP00')
        pop00.add_argument('--output-dir', required=True, help='Nowy katalog pakietu POP00')
        pop00.add_argument('--json', action='store_true', help='Odpowiedź JSON')
        topics = sub.add_parser('tematy', help='Zbuduj pakiet TEMATY dla jednego tematu (ADR-010)')
        topics.add_argument('--manifest', required=True, help='Manifest przypiętych wejść TEMATY (tematy-sources.json)')
        topics.add_argument('--config', required=True, help='Konfiguracja metody (tematy.json)')
        topics.add_argument('--topic', required=True, help='Plik tematu, np. config/generator/tematy/morze.json')
        topics.add_argument('--output-dir', required=True, help='Nowy, nieistniejący katalog pakietu TEMATY')
        topics.add_argument('--json', action='store_true', help='Odpowiedź JSON')
        morph = sub.add_parser('morph-index', help='Indeks morfologii SGJP dla form BROAD (format v1)')
        morph.add_argument('--broad', required=True, help='Lista BROAD (.txt.gz)')
        morph.add_argument('--sgjp', required=True, help='Eksport SGJP (.tab.gz)')
        morph.add_argument('--broad-lexicon-id', required=True, help='Id leksykonu w serwerze, np. pl-broad-20261011')
        morph.add_argument('--broad-dawg-sha256', required=True, help='SHA-256 pliku .dawg z serwera (64 hex)')
        morph.add_argument('--out', required=True, help='Nowy plik .bin; istniejący nie jest nadpisywany')
        morph.add_argument('--json', action='store_true', help='Odpowiedź JSON')
        args = parser.parse_args(argv)
        if args.command == 'inspect-sources':
            checked = inspect_sources(args.manifest)
            result['result'] = {k: v for k, v in checked.items() if k != 'manifest'}
        elif args.command == 'build':
            from .build import build
            result['result'] = build(args.manifest, args.run_dir)
        elif args.command == 'explain':
            if args.variant == 'pop00':
                if not args.pop00_dir:
                    raise GeneratorError('Wariant pop00 wymaga --pop00-dir', 2)
                from .pop00 import explain_pop00
                result['result'] = explain_pop00(args.pop00_dir, args.run_dir, args.word)
            elif args.variant in ('pop', 'pop0'):
                if not args.pop_dir:
                    raise GeneratorError('Wariant pop/pop0 wymaga --pop-dir', 2)
                from .explain import explain_pop
                result['result'] = explain_pop(args.pop_dir, args.run_dir, args.word, args.variant)
            else:
                from .explain import explain
                result['result'] = explain(args.run_dir, args.word, args.variant)
        elif args.command == 'verify':
            from .verify import verify
            report = verify(args.run_dir, args.peer_run, args.review)
            result['result'] = report
            if report['verdict'] != 'VERIFIED':
                result['status'] = 'refused'
                blocked = [k for k, item in report['checks'].items() if item['status'] != 'pass']
                print('Verify odmówił VERIFIED; blokady: ' + ', '.join(blocked), file=sys.stderr)
                return _finish(argv, command, result, 5)
        elif args.command == 'pop':
            from .pop import build_package
            result['result'] = build_package(args.manifest, args.config, args.output_dir, args.run_dir,
                                             args.release_dir)
        elif args.command == 'pop00':
            from .pop00 import build_package
            result['result'] = build_package(args.manifest, args.config, args.output_dir)
        elif args.command == 'tematy':
            from .tematy import build_package
            result['result'] = build_package(args.manifest, args.config, args.topic, args.output_dir)
        elif args.command == 'morph-index':
            from .morph_index import write_index
            result['result'] = write_index(args.broad, args.sgjp, args.broad_lexicon_id,
                                           args.broad_dawg_sha256, args.out)
        elif args.command == 'export':
            from .export import export
            result['result'] = export(args.run_dir, args.output_dir)
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
    return _finish(argv, command, result, code)


def _finish(argv, command, result, code):
    if '--json' in argv:
        print(dumps(result))
    elif command == 'verify' and 'result' in result:
        from .verify import format_verification
        print(format_verification(result['result']))
    elif result['status'] == 'ok':
        if command == 'explain' and result['result'].get('method') == 'pop00-v1':
            from .pop00 import format_pop00_explanation
            print(format_pop00_explanation(result['result']))
        elif command == 'explain' and 'reason' in result['result']:
            from .explain import format_pop_explanation
            print(format_pop_explanation(result['result']))
        elif command == 'explain':
            from .explain import format_explanation
            print(format_explanation(result['result']))
        elif command == 'pop':
            found = result['result']
            cut = found['thresholds']['pop']
            # pop-v3: progi punktacji są tymczasowymi stałymi (#6), nie limitami leksemów.
            score = ''.join(f"\nPróg {name.upper()}: punktacja ≥ {item['score']} (stała tymczasowa, {item['provisional']})"
                            for name, item in (('pop', cut), ('pop0', found['thresholds']['pop0'])) if 'score' in item)
            print(f"Pakiet POP (BUILT, {found['method']}): {found['output_dir']}\n"
                  f"POP: {found['forms']['pop']} form, {cut['lexemes']} leksemów; "
                  f"POP0: {found['forms']['pop0']} form, {found['thresholds']['pop0']['lexemes']} leksemów{score}")
        elif command == 'pop00':
            found = result['result']
            print(f"Pakiet POP00 (BUILT, {found['method']}): {found['output_dir']}\n"
                  f"{found['forms']} form; {found['selected_lexemes']} leksemów; próg wybranych form 0,1 IPM")
        elif command == 'tematy':
            found = result['result']
            n, lex = found['liczby'], found['przeciecia']['leksemy']['razem']
            words, verdict = found['slowa_oczywiste'], found['werdykt']
            inland = found['srodladowe']['kandydaci_t3']
            print(f"Pakiet TEMATY (BUILT, {found['method']}, {found['wersja_tematu']}): {found['output_dir']}\n"
                  f"Wpisy: {n['wpisy']} (T1 {n['warstwy']['T1']}, T2 {n['warstwy']['T2']}, T3 {n['warstwy']['T3']}, "
                  f"D {n['warstwy']['D']}); "
                  f"formy: {n['formy']}\n"
                  f"Leksemy w POP: {lex['pop']['liczba']} ({lex['pop']['procent']}%); "
                  f"w POP00 (POP0): {lex['pop00']['liczba']} ({lex['pop00']['procent']}%)\n"
                  f"Test {words['lista']} słów: {words['razem']['pokryte']} ({words['razem']['procent']}%), "
                  f"próg {words['prog']}\n"
                  f"Śródlądowe w T3: {inland['srodladowe']} z {inland['hasla']} haseł\n"
                  f"Werdykt automatyczny: {verdict['automatyczny']}"
                  + (f" ({', '.join(verdict['niespelnione'])})" if verdict['niespelnione'] else '')
                  + '; progi z ocen czekają na przegląd')
        elif command == 'morph-index':
            found = result['result']
            print(f"Indeks: {found['out']}\n"
                  f"Formy z analizą: {found['forms_with_analysis']} z {found['broad_forms']}\n"
                  f"Reguły: {found['rules']}, listy: {found['rule_lists']}, końcówki: {found['lemma_endings']}\n"
                  f"Bajty: {found['bytes']}, gzip -9: {found['gzip_bytes']}\n"
                  f"SHA-256: {found['sha256']}")
        else:
            print('Kontrola zakończona: ' + dumps(result.get('result', {})))
    return code
