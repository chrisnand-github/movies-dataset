import streamlit as st
from collections import defaultdict
import re
import math
import os
import glob

# Function to convert text to uppercase
def convert_to_uppercase(text):
    return text.upper()


def pop(stack):
    """ Pop last item from stack, when exit are encountered in hierarchical config"""
    try:
        stack.pop()
    except Exception as err:
        print("ERROR: Unable to flush stack - %s" % err)
def output(stack):
    """ Out flat config lines """
    output = " ".join(stack)
    #print(output)
    return output
def sros_flatten(data):
    stack = []
    exit_detected = False
    indent = 0
    new_conf = ""
    for line in data.lstrip().splitlines():
        l = len(line) - len(line.lstrip())
        nxt_indent = math.ceil(float(l / 4))
        if line.startswith(("#", "echo")) or line.strip() == "":
            pass
        elif line.strip() == "exit all":
            new_conf = new_conf + "\n" + output(stack)
        else:
            if nxt_indent == 0 and line.strip() == "configure":
                new_line = str("/") + str(line.strip())
                stack.append(new_line)
            elif nxt_indent > indent:
                if line.strip() != "configure" and len(stack) == 0:
                    stack.insert(0, "/configure")
                stack.append(line.lstrip())
            elif nxt_indent == indent:
                if line.strip() != "exit":
                    if exit_detected:
                        stack.append(line.strip())
                    else:
                        if len(stack) != 0:
                            new_conf = new_conf + "\n" + output(stack)
                            pop(stack)
                            stack.append(line.strip())
                        else:
                            stack.insert(0, "/configure")
                            stack.append(line.strip())
                    exit_detected = False

            else:
                if line.strip() == "exit":
                    if not exit_detected:
                        new_conf = new_conf + "\n" + output(stack)
                        del stack[-2:]
                    else:
                        pop(stack)
                    exit_detected = True

                else:
                    new_conf = new_conf + "\n" + output(stack)
                    exit_detected = False
                    pop(stack)
            indent = nxt_indent

    return new_conf

def read_txt_file(file):
    #print(file)
    lines = [line + '\n' for line in file.splitlines()]
    #lines = file.splitlines()


    # Find the index of the lines containing "# Generated" and "# Finished"
    generated_index = None
    finished_index = None

    for i, line in enumerate(lines):
        if "# Generated" in line:
            generated_index = i
        elif "# Finished" in line:
            finished_index = i
            break  # Stop searching once we find the "# Finished" line

    # Extract text between the lines containing "# Generated" and "# Finished"
    if generated_index is not None and finished_index is not None:
        generated_date = lines[generated_index].strip().replace("# Generated ", "")
        finished_date = lines[finished_index].strip().replace("# Finished ", "")
        text_between = "".join(lines[generated_index + 1:finished_index])

        return generated_date, finished_date, text_between
    else:
        return None, None, None
def stop_exit_all(data):
    clean =""
    for line in data.split("\n" or "\r"):
        clean += line+"\n"
        if line == "exit all":
            break
    return (clean)
def seperation_data(data):
    pattern = r"#--------------------------------------------------"
    matches = re.split(pattern, data)
    #print(matches[6])
    config = {}
    z = ""
    last = ""
    for i in range(len(matches)):
        if i == 0:
            print("")
        elif (i % 2) != 0:
            #print(matches[i])
            z = re.findall('"([^"]*)"', matches[i])[0]
            config[z] = "x"
            #print(z)
            last =z
        else:
            # print(matches[i])
            # print(matches[i-1])
            config.update({z: matches[i]})
    # print(config)
    config.update({last:stop_exit_all(config.get(last))})
    return(config)



#file_path = "D:/9 sites/172.16.243.19/2024.07.18-02.01.23.681/cf3,/MBHQAIBS0444.cfg"
file_path = "D:/9 sites/172.16.246.146/2024.07.18-02.01.36.390/cf3,/MBJQAKHR1689.cfg"
#file_path = "console_2852.txt"  # Change this to the path of your .txt file
#generated_date, finished_date, text_between = read_txt_file(file_path)
#print(text_between)


#seperation=seperation_data(text_between)
#print(seperation.get("Service Configuration"))

#a = sros_flatten(seperation.get("Service Configuration"))
#print(sros_flatten(seperation.get("Service Configuration")))
def find(data,input):
    txt = ""
    for line in data.lstrip().splitlines():
        if input in line:
            #print(line)
            txt=txt+line+"\n"
    return(txt)
#match(a)
#b= find_sap(a)
#print(b)


def parse_vprn_data_SAP(txt):
    vprn_dict = defaultdict(lambda: defaultdict(set))

    # Split the input text into lines
    lines = txt.strip().split('\n')

    # Regular expression to extract vprn_id, interface, and sap
    pattern = re.compile(r'/configure service vprn (\d+) customer \d+ create interface "(.*?)" create sap (.*?) ')

    for line in lines:
        match = pattern.search(line)
        if match:
            vprn_id, interface, sap = match.groups()
            vprn_dict[vprn_id][interface].add(sap)

    # Convert sets to list of dictionaries
    result = {}
    for vprn_id, interfaces in vprn_dict.items():
        result[vprn_id] = [{interface: list(saps)[0]} for interface, saps in interfaces.items()]

    return result

#vprn_data = parse_vprn_data(b)
#print(vprn_data)

def find_rd_rt(data):
    txt = ""
    for line in data.lstrip().splitlines():
        if "vrf-target" in line or "route-distinguisher" in line:
            #print(line)
            txt=txt+line+"\n"
    return(txt)

#print(find_rd_rt(a))
#c= find_rd_rt(a)


def parse_vprn_data_RD(data):
    vprn_dict = {}
    lines = data.strip().split('\n')

    for line in lines:
        # Extract vprn_id
        vprn_id_match = re.search(r'/configure service vprn (\d+)', line)
        if vprn_id_match:
            vprn_id = vprn_id_match.group(1)

        # Extract route-distinguisher
        rd_match = re.search(r'route-distinguisher ([^ ]+)', line)
        if rd_match:
            rd = rd_match.group(1)
            if vprn_id not in vprn_dict:
                vprn_dict[vprn_id] = [rd, None]
            else:
                vprn_dict[vprn_id][0] = rd

        # Extract vrf-target
        rt_match = re.search(r'vrf-target target:([^ ]+)', line)
        if rt_match:
            rt = rt_match.group(1)
            if vprn_id not in vprn_dict:
                vprn_dict[vprn_id] = [None, rt]
            else:
                vprn_dict[vprn_id][1] = rt

    return vprn_dict



def read_name_from_line(txt):
    try:
        lines = txt.strip().split('\n')

        if len(lines) > 1:
            raise ValueError("Error: More than one line provided.")

        pattern = re.compile(r'/configure system name "(.*?)"')
        match = pattern.search(lines[0])

        if match:
            return match.group(1)
        else:
            raise ValueError("Error: No name found in the provided line.")

    except ValueError as e:
        return str(e)


import os


# def find_all_txt_files(directory):
#     txt_files = []
#
#     for root, dirs, files in os.walk(directory):
#         for file in files:
#             if file.endswith(".cfg") and "bof" not in file:
#                 txt_files.append(os.path.join(root, file))
#
#     return txt_files

from collections import defaultdict
def parse_vprn_data_DHCP(txt):
    vprn_dict = defaultdict(dict)

    # Split the input text into lines
    lines = txt.strip().split('\n')

    # Regular expression to extract vprn_id, interface, and dhcp servers
    pattern = re.compile(
        r'/configure service vprn (\d+) customer \d+ create interface "(.*?)" create dhcp server ([\d. ]+)')

    for line in lines:
        match = pattern.search(line)
        if match:
            vprn_id, interface, dhcp_servers = match.groups()
            dhcp_servers_list = dhcp_servers.split()  # Split the dhcp servers into a list
            vprn_dict[vprn_id][interface] = dhcp_servers_list

    return dict(vprn_dict)


def parse_vprn_mtu_data(txt):
    vprn_dict = defaultdict(dict)

    # Split the input text into lines
    lines = txt.strip().split('\n')

    # Regular expression to extract vprn_id, interface, and ip-mtu
    pattern = re.compile(r'/configure service vprn (\d+) customer \d+ create interface "(.*?)" create ip-mtu (\d+)')

    for line in lines:
        match = pattern.search(line)
        if match:
            vprn_id, interface, ip_mtu = match.groups()
            vprn_dict[vprn_id][interface] = ip_mtu
    return dict(vprn_dict)

def parse_vprn_data_address(input_text):
    vprn_dict = defaultdict(list)

    # Regular expression to extract vprn_id, interface, and address
    pattern = re.compile(r'/configure service vprn (\d+) customer \d+ create interface "(.*?)" create address (.*?)$')

    # Split the input text into lines
    lines = input_text.strip().split('\n')

    for line in lines:
        match = pattern.search(line)
        if match:
            vprn_id, interface, address = match.groups()
            vprn_dict[vprn_id].append({interface: address})

    return dict(vprn_dict)
def parse_vprn_static_routes(input_text):
    vprn_dict = defaultdict(list)

    # Regular expression to extract vprn_id, static-route-entry, and next-hop
    pattern = re.compile(r'/configure service vprn (\d+) name "\d+" customer \d+ create static-route-entry (.*?) next-hop (.*?) no shutdown')

    # Split the input text into lines
    lines = input_text.strip().split('\n')

    for line in lines:
        match = pattern.search(line)
        if match:
            vprn_id, static_route_entry, next_hop = match.groups()
            vprn_dict[vprn_id].append({static_route_entry: next_hop})

    return dict(vprn_dict)

# Example usage
# directory = "D:/make_service/"
# txt_files = find_all_txt_files(directory)
# print(txt_files)

def find_qos(input):
    qos_ingress = {'17815':'120','17804':'104','17813':'103','17812':'102','55000':'104'}
    txt = qos_ingress[input]
    return(txt)

def find_name(input):
    qos_ingress = {'17815':'17815','17804':'17804','17813':'17813','17812':'17812','55000':'ENT-4G-5G_Public'}
    txt = qos_ingress[input]
    return(txt)
def find_desc(input):
    qos_ingress = {'17815':'Huawei OAM VPRN','17804':'eNB IPsec Public eUTRAN VPRN','17813':'eNB_RNC_IuB_VPRN','17812':'BTS_BSC_Abis_VPRN','55000':'ENT 4G-5G Public Service'}
    txt = qos_ingress[input]
    return(txt)

def make_service(name,sap,rd,dhcp,mtu,address,static):
    txt=""
    txt+=f"{name}\n"
    for vprn_id, interfaces in sap.items():
        txt+=f"{vprn_id}\n"
        #print(address)
        txt+=(f"""        vprn {vprn_id} name {find_name(vprn_id)} customer 1 create\n""")
        txt+=(f'''            description "{find_desc(vprn_id)}"\n''')
        txt+=("            autonomous-system 48728\n")
        #print(dhcp)
        for i,interface in enumerate(interfaces):
            for key,value in interface.items():
                txt+=(f"""            interface {key} create\n""")
                if vprn_id in address:
                    if key in address[vprn_id][i]:
                        txt+=(f"""                address {address[vprn_id][i][key]}\n""")
                if vprn_id in dhcp:
                    #print(dhcp[vprn_id])
                    if key in dhcp[vprn_id]:
                        txt+=("""                dhcp\n""")
                        txt_static= ' '.join(str(element) for element in dhcp[vprn_id][key])
                        txt+=(f"""                    server {txt_static}\n""")
                        txt+=("""                    no shutdown
                exit\n""")
                if vprn_id in mtu:
                    #print(mtu[vprn_id])
                    if key in mtu[vprn_id]:
                        txt+=(f"""                ip-mtu {mtu[vprn_id][key]}\n""")
                txt+=(f"""                sap {value} create\n""")
                txt+=(f"""                    ingress
                        qos {find_qos(vprn_id)}
                    exit\n""")
                if vprn_id !='17815':
                    txt+=(f"""                    egress
                        vlan-qos-policy {find_qos(vprn_id)}
                        egress-remark-policy {find_qos(vprn_id)}
                    exit\n""")
                txt+=("""                exit
            exit\n""")

        if vprn_id in static:
            txt+=(static[vprn_id])
            for key, value in static[vprn_id].items():
                txt+=(key,value)


        txt+=("""            bgp-ipvpn
                mpls
                    auto-bind-tunnel\n""")
        if vprn_id == '55000':
            txt+=("""                        resolution-filter
                        exit
                        resolution filter\n""")
        else:
            txt+=("""                        resolution any\n""")
        txt+=("""                    exit\n""")
        txt+=(f"""                    route-distinguisher {rd[vprn_id][0]}\n""")
        txt+=(f"""                    vrf-target target:{rd[vprn_id][1]}\n""")
        txt+=("""                    no shutdown
                exit
            exit
            no shutdown
        exit\n""")
    return(txt)



def find_all_instances(dictionaries):
    import re
    pattern = re.compile(r"ISIS \(Inst: (\d)\) Configuration")
    instances = []

    for key in dictionaries.keys():
        match = pattern.match(key)
        if match:
           instances.append((int(match.group(1))))

    if instances:
        return(instances)
        instance_numbers = sorted(set(instance[0] for instance in instances))
        #print("Instance numbers:", instance_numbers)
        #print("All instances:")
        #for instance in instances:
        #    print(f"Instance {instance[0]}: {instance[1]}")
    else:
        print("No instances found.")


def final_service(input):
    generated_date, finished_date, text_between = read_txt_file(txt_before)
    seperation = seperation_data(text_between)
    service_txt = sros_flatten(seperation.get("Service Configuration"))
    system_txt = sros_flatten(seperation.get("System Configuration"))
    name = find(system_txt, "name")
    name_result = read_name_from_line(name)
    # print(name_result)
    address = find(service_txt, "address")
    # print(address)
    address_result = parse_vprn_data_address(address)
    # print(address_result)
    sap = find(service_txt, "sap")
    # print(sap)
    sap_result = parse_vprn_data_SAP(sap)
    # print(sap_result)
    rd = find_rd_rt(service_txt)
    rd_result = parse_vprn_data_RD(rd)
    # print(rd_result)
    # print(seperation.get("System Configuration"))
    # isis_txt = sros_flatten(seperation.get("ISIS (Inst: 3) Configuration"))
    # print(isis_txt)
    dhcp = find(service_txt, "dhcp server")
    dhcp_result = parse_vprn_data_DHCP(dhcp)
    # print(dhcp)
    # print(dhcp_result)
    mtu = find(service_txt, "ip-mtu")
    ipmtu_result = parse_vprn_mtu_data(mtu)
    # print(ipmtu_result)
    static = find(service_txt, "next-hop")
    # print(static)
    static_result = parse_vprn_static_routes(static)
    # print(static_result)
    print_result = make_service(name_result, sap_result, rd_result, dhcp_result, ipmtu_result, address_result,
                                static_result)
    return(print_result)


# Streamlit App
def main():
    # Title of the app
    st.title("Text File Uppercase Converter")

    # Create a textbox for input text
    st.write("Paste your text here:")
    input_text = st.text_area("Input Text", height=200)

    # Create a button to trigger the conversion
    if st.button("Convert"):
        if input_text:
            # Call the conversion function
            #output_text = final_service(input_text)
            output_text = final(input_text)
            # Display the output on the right side
            st.write("### Converted Text:")
            st.text_area("Output Text", output_text, height=200)
        else:
            st.write("Please paste some text to convert.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
