
data = "cmd#set_snmac#1122334455677B9#883B8B010AE4"

head, cmd, sn, mac = string.match(data, "(%w+)#(%w+_%w+)#(%w+)#(%w+)")

print(head)
print(cmd)
print(sn)
print(mac)
