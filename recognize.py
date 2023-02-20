from collections import OrderedDict

def recognize_character(sound):
    confusable_sounds = {
        'a': ['ay', 'ai', 'ei', 'ah', 'pa', 'a a', 'a'],
        'b': ['bă', 'be', 'bee', 'b'],
        'c': ['că', 'sea', 'see', 'si', 's', 'c'],
        'd': ['da', 'de', 'dee', 'des', 'the', 'd'],
        'e': ['ee', 'eee', 'e e', 'ei', 'i', 'e'],
        'f': ['fă', 'if', 'ef', 'eff', 'film', 'f'],
        'g': ['ge', 'gee', 'gg', 'g g', 'g'],
        'h': ['aitch', 'hai', 'hush', 'high', 'aș', 'haș', 'us', 'h'],
        'i': ['eye', 'ai', 'hai', 'e', 'îi', 'i i', 'i'],
        'j': ['jay', 'j', 'jiu'],
        'k': ['kay', 'ca', 'că', 'chei', 'kappa', 'kapa', 'capa', 'k'],
        'l': ['el', 'le', 'ell', 'ellie', 'ali', 'l'],
        'm': ['em', 'mă', 'ema', 'm'],
        'n': ['en', 'ana', 'nu', 'an', 'n'],
        'o': ['oh', 'ou', 'oh', 'aw', 'o'],
        'p': ['pea', 'pee', 'p p', 'p'],
        'q': ['cue', 'queue', 'eu', 'keo', 'chiu', 'q'],
        'r': ['ar', 're', 'air', 'el', 'aer', 'r'],
        's': ['es', 'est', 'test', 'teste', 'ass', 'esc', 'ask', 'să', 's'],
        't': ['tea', 'tee', 'teo', 'tu', 'te', 't u', 't'],
        'u': ['you', 'ew', 'ooo', 'oo', 'hu', 'who', 'u'],
        'v': ['vee', 'vei', 'veri', 'very', 'vă', 'v'],
        'w': ['double-u', 'dublu-v', 'w'],
        'x': ['ex', 'ax', 'pix', 'x'],
        'y': ['why', 'y y', 'y'],
        'z': ['zee', 'zet', 'zed', 'zedge', 'zi', 'zen' 'z'],
    }
    possible_letters = []
    for letter in confusable_sounds:
        if sound in confusable_sounds[letter]:
            possible_letters.append(letter)
    return possible_letters

def recognize_letter(recognised_dict, guessed_letters):
    possible_letters_freq = {}
    for alternative in recognised_dict['alternative']:
        for letter in recognize_character(alternative['transcript'].lower()):
            if letter in possible_letters_freq:
                possible_letters_freq[letter] += 1
            else:
                possible_letters_freq[letter] = 1
            if 'confidence' in alternative and alternative['confidence'] > 0.55:
                possible_letters_freq[letter] += 1
            if alternative['transcript'].isalpha() and len(alternative['transcript']) == 1:
                possible_letters_freq[letter] += 1
    if len(possible_letters_freq) == 0:
        return ""
    recognized_letter = max(possible_letters_freq, key=possible_letters_freq.get)
    sorted_dict = OrderedDict(sorted(possible_letters_freq.items(), key=lambda t: t[1], reverse=True))
    print(sorted_dict)
    for elem in sorted_dict:
        if elem.upper() in guessed_letters:
            continue
        else:
            recognized_letter = elem.upper()
            break
    return recognized_letter.upper()
