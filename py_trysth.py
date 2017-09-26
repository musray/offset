seq = ['1', '2', '3', '4', '5']

def func(order):
    if order in seq:
        print('test passed')


d = { '1': ['1', '2', '3'], '2': ['11', '22', '33'], '3': ['111', '222', '333'] }

def find_key(order):
    result = False
    for key, value in d.items():
        print(value)
        if order in value:
            result = key

    return result

print(find_key('11'))
print(find_key('1111'))
