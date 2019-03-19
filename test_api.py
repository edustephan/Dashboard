import PyU4V


conn = PyU4V.U4VConn(server_ip = '172.21.25.210', port=8443, verify=False, username='smc', password='smc')
version = conn.common.get_uni_version()
array_list=conn.common.get_array_list()

print(version)
print("Array List: ", array_list)

#https://172.21.25.210:8443/univmax/restapi/sloprovisioning/symmetrix/000197700501