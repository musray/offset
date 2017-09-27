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

# print(find_key('11'))
# print(find_key('1111'))

NET_NODE_RELATION = {
    '0': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '21', '18', '19', '23', '24', '33', '48', '49', '63'],
    '1': ['11', '12', '13', '14', '15', '16', '17', '18', '19', '25', '26', '27', '28', '29', '30', '31', '32'],
    '2': ['41', '42', '43', '44', '45', '47', '48', '49', '55', '56', '57', '58', '59', '60', '61', '62'],
    '3': ['10', '22', '25', '27', '28', '29', '30', '31', '55', '57', '58', '59', '61', '60']
}

# for key, value in NET_NODE_RELATION.items():
#     print( key )

import re

name = 'netdev_199.csv'

matchObj = re.findall(r'\d+', name)
print(matchObj)

