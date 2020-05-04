import random


def small_talk(want):
    prefixes = ['', '那么，', '', '咳咳，', '', '嘿嘿，', '', '啊...', '', '嗯...',
                '我看看，', '', '我看下啊...', '', '嚯！', '', '嗯哼，', '', '嗯呢，',
                '', '哦哦，', '', '哦唷', '', '啧啧，', '', '喔，', '', ]
    suffixes = ['对吧', '', '狸']
    middle = ['的话，', '', ]
    if want == 'prefix':
        result = random.choice(prefixes)
    elif want == 'suffix':
        result = random.choice(suffixes)
    elif want == 'middle':
        result = random.choice(middle)
    return result


def lify(d):
    content = ''
    mid = small_talk('middle')
    for k in d:
        if isinstance(d[k], dict):
            prefix = small_talk('prefix')
            sentence = f'{prefix} **{k}** {mid}...\n'
            content += sentence
            content += lify(d[k])
        else:
            mid = small_talk('middle')
            prefix = small_talk('prefix')
            suffix = small_talk('suffix')
            sentence = f'{prefix}{k}{mid}是** {d[k]} **{suffix}\n'
            content += sentence

    return content


def ill_minded(p):
    result = ''
    k = int(len(p)*random.random())
    if k < 2:
        k = 2
    ill = random.choices(p, k=k)
    for i in ill:
        result += i
    return result


def deaf(msg):
    return f'{small_talk("prefix")}你说{ill_minded(msg)}？听见了狸！'

