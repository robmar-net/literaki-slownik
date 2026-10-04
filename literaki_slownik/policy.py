"""Potwierdzona pisownia growa i profil; bez aktywacji polityki językowej."""
import unicodedata

ALPHABET = 'aąbcćdeęfghijklłmnńoóprsśtuwyzźż'
VERSION = 'diagnostic-mechanics-v1'


def spelling_checks(original):
    """Ocena źródłowego zapisu, zanim powstanie małoliterowy klucz."""
    uppercase = any(character.isupper() for character in unicodedata.normalize('NFC', original))
    return [{'rule_id': 'game-required-uppercase-v1',
             'status': 'reject' if uppercase else 'accept',
             'message': 'Źródłowy zapis wymaga wielkich liter.' if uppercase else
                        'Źródłowy zapis nie zawiera wielkich liter; pozostałe reguły oceniane osobno.',
             'evidence': ['docs/generator/ortografia.md']}]


def assess_profile(original):
    nfc = unicodedata.normalize('NFC', original)
    key = unicodedata.normalize('NFC', nfc.lower())
    invalid = sorted(set(key) - set(ALPHABET))
    checks = [
        {'rule_id': 'profile-pl-alphabet-v1', 'status': 'reject' if invalid else 'accept',
         'message': 'Znaki poza alfabetem płytek.' if invalid else 'Alfabet płytek zgodny.',
         'evidence': ['config/generator/profile.json']},
        {'rule_id': 'profile-pl-length-v1', 'status': 'accept' if 2 <= len(key) <= 15 else 'reject',
         'message': 'Wymagana długość 2–15 znaków po NFC/lower.',
         'evidence': ['config/generator/profile.json']},
    ]
    return {'status': 'reject' if any(c['status'] == 'reject' for c in checks) else 'accept',
            'version': 'pl-v1', 'original': original, 'nfc': nfc, 'game_key': key,
            'length': len(key), 'invalid_characters': invalid, 'checks': checks}
