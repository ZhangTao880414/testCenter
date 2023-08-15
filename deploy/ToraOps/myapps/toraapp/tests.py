from django.test import TestCase

# Create your tests here.

# data = {"cust_name":'zhangwei', 'cust_no':89}
# print(type(data))
# print('cust_naame' not in data.keys())

vpn_name='name1name2'
new=vpn_name.replace(';', '_')
print(new)