from src.ec2.vpc import VPC
from src.ec2.ec2 import EC2
from src.ec2.elb import ELB
from src.client_locator import EC2Client

"""
This Script is for ap-southeast-1 region (Singapore). If you use for another Region, you need to change the availability
zones of Subnets,VPC Peering Connection Region Id,AMI Image Id. For the numbers of EC2 instance to be launch you need to
specify the MinCount and MaxCount 
"""
print("""       ##########################################################
                #                                                        #           
                #  DEPLOYING AWS INFRASTRUCTURE ... FUCK YOU JEFF BEZOS  #
                #                                                        #
                ##########################################################      """)

ec2_client = EC2Client().get_client()
vpc = VPC(ec2_client)

cidrblock_1 = '10.10.0.0/16'
vpc1_response = vpc.create_vpc(cidrblock_1)

vpc1_id = vpc1_response['Vpc']['VpcId']
vpc1_name = 'vpc01'
vpc.add_tag(vpc1_id,vpc1_name)

igw_response = vpc.create_igw()
igw_id = igw_response['InternetGateway']['InternetGatewayId']

vpc.attach_igw(igw_id,vpc1_id)

#Public Subnet
public_subnet = vpc.create_subnet(vpc1_id,'apse1-az2','10.10.0.0/20')
public_subnet_id = public_subnet['Subnet']['SubnetId']

#Private Subnet
private_subnet = vpc.create_subnet(vpc1_id,'apse1-az1','10.10.16.0/20')
private_subnet_id = private_subnet['Subnet']['SubnetId']

#Public Route Table
public_route_table = vpc.create_route_table(vpc1_id)
public_route_table_id = public_route_table['RouteTable']['RouteTableId']
vpc.add_tag(public_route_table_id,'vpc01-public')

#Private Route Table
private_route_table = vpc.create_route_table(vpc1_id)
private_route_table_id = private_route_table['RouteTable']['RouteTableId']
vpc.add_tag(private_route_table_id,'vpc01-private')

#Public  Route to Internet Gateway
vpc.create_public_route(public_route_table_id,'0.0.0.0/0',igw_id)

#Auto Assign Public IP on Public Subnet
vpc.allow_auto_assing_ip_address_for_subnet(public_subnet_id)

#Allocate Elastic IP
allocation_response = vpc.allocate_elastic_ip()
allocation_response_id = allocation_response['AllocationId']

#NAT Gateway
nat_gw_response = vpc.create_nat_gateway(allocation_response_id,public_subnet_id)
nat_gw_id  = nat_gw_response['NatGateway']['NatGatewayId']

#Add Tag to 'vpc01' Nat Gateway

vpc.add_tag(nat_gw_id,'vpc01-nat')

# Associate Route Talbe with Public Subnet
vpc.associate_subnet_with_route_table(public_subnet_id,public_route_table_id)

#Associate Route Table with Private Subnet
vpc.associate_subnet_with_route_table(private_subnet_id,private_route_table_id)

#Private Route to Nat Gateway
vpc.create_private_route_to_nat_igw(private_route_table_id,'0.0.0.0/0',nat_gw_id)

#######################################################################################################

cidrblock_2 = '192.168.0.0/16'
vpc2_response = vpc.create_vpc(cidrblock_2)

vpc2_id = vpc2_response['Vpc']['VpcId']
vpc2_name = 'vpc02'

vpc.add_tag(vpc2_id,vpc2_name)

private_subnet_2 = vpc.create_subnet(vpc2_id,'apse1-az3','192.168.0.0/20')
private_subnet_id_2 = private_subnet_2['Subnet']['SubnetId']

private_route_table_2 = vpc.create_route_table(vpc2_id)
private_route_table_id_2 = private_route_table_2['RouteTable']['RouteTableId']
vpc.associate_subnet_with_route_table(private_subnet_id_2,private_route_table_id_2)

vpc.add_tag(private_route_table_id_2,'vpc02-private')

############### VPC PEERING CONNECTION VPC01 VIA VPC02 ###########################

vpc_peering_connection = vpc.create_vpc_peering_conn(vpc1_id,vpc2_id)
vpc_peering_connection_id = vpc_peering_connection['VpcPeeringConnection']['VpcPeeringConnectionId']

vpc_peering_connection_name = 'vpc01-to-vpc02'
vpc.add_tag(vpc_peering_connection_id,vpc_peering_connection_name)

vpc.accept_vpc_peering_connection(vpc_peering_connection_id)

################### VPC PEERING CONNECTION ROUTES #################################

#vpc01
vpc.create_route_to_peering_connection(private_route_table_id,'192.168.0.0/16',vpc_peering_connection_id)

#vpc02
vpc.create_route_to_peering_connection(private_route_table_id_2,'10.10.0.0/16',vpc_peering_connection_id)




############### EC2 ###############

ec2 = EC2(ec2_client)

#KeyPair
key_pair_name = 'CloudKey'
key_pair_response = ec2.create_key_pair(key_pair_name)
print('Key Pair Created '+key_pair_name+str(key_pair_response))

#################################### VPC01 ##################################

#Public Security Group
public_security_group_name = 'vpc01-Public-SG'
public_security_group_description = 'Public Security Group for Public Subnet Internet Access'
public_security_group_response = ec2.create_security_group(public_security_group_name,public_security_group_description,vpc1_id)
public_security_group_id = public_security_group_response['GroupId']

#Adding Rules to Public Security Group
ec2.add_rule_to_security_group(public_security_group_id,'0.0.0.0/0')

user_data01 = """#!/bin/bash
                yum install httpd -y
                systemctl start httpd
                systemctl enable httpd
                echo LOAD BALANCING FOR WEB01 > /var/www/html/index.html
                systemctl restart httpd """

user_data02 = """#!/bin/bash
                yum install httpd -y
                systemctl start httpd
                systemctl enable httpd
                echo LOAD BALANCING FOR WEB02 > /var/www/html/index.html
                systemctl restart httpd """

#Launch EC2 Instance in Public Subnet
ami_id = 'ami-0cd31be676780afa7' #AmazonLinux (64bits x 86)
instance_type = 't2.micro'
instance01_response = ec2.launch_ec2_instance(ami_id,key_pair_name,1,1,instance_type,public_security_group_id,public_subnet_id,user_data01)
instance01_image_id = instance01_response['Instances'][0]['InstanceId']
instance02_response = ec2.launch_ec2_instance(ami_id,key_pair_name,1,1,instance_type,public_security_group_id,public_subnet_id,user_data02)
instance02_image_id = instance02_response['Instances'][0]['InstanceId']

#Private Security Group (vpc01)
private_security_group_name = 'vpc01-Private-SG'
private_security_group_description = 'Private Security Group'
private_security_group_response = ec2.create_security_group(private_security_group_name,private_security_group_description,vpc1_id)
private_security_group_id = private_security_group_response['GroupId']

#Adding Rules to Private Security Group (vpc01)
ec2.add_rule_to_security_group(private_security_group_id,'10.10.0.0/20')

#Launch EC2 Instance in Private Subnet
ec2.launch_ec2_instance(ami_id,key_pair_name,1,1,instance_type,private_security_group_id,private_subnet_id,"""#!/bin/bash \n yum update -y""")
################################## VPC02 ###################################

#Private Security Group (vpc02)
private_security_group_name_2 = 'vpc02-Private-SG'
private_security_group_description_2 = 'Private Security Group'
private_security_group_response_2 = ec2.create_security_group(private_security_group_name_2,private_security_group_description_2,vpc2_id)
private_security_group_id_2 = private_security_group_response_2['GroupId']

#Adding Rules to Private Security Group (vpc02)
ec2.add_rule_to_security_group(private_security_group_id_2,'10.10.16.0/20')

#Launch EC2 Instance in Private Subnet

ec2.launch_ec2_instance(ami_id,key_pair_name,1,1,instance_type,private_security_group_id_2,private_subnet_id_2,"""#!/bin/bash\nyum update -y""")

############################### LOAD BALANCING ################################
elb = ELB('elbv2')

#LOAD BALANCING
elb_name = 'myelb'
load_balancer_response = elb.load_balancer(elb_name,public_subnet_id,private_subnet_id,public_security_group_id)
load_balancer_arn = load_balancer_response['LoadBalancers'][0]['LoadBalancerArn']

#TARGET GROUP FOR VPC01
target_group_name = 'myelb-tg'
target_group_response = elb.target_group(target_group_name,vpc1_id)
target_group_arn = target_group_response['TargetGroups'][0]['TargetGroupArn']

#REGISTER TARGETS
register_target_response = elb.register_targets(target_group_arn, instance01_image_id, instance02_image_id)

#ELB Listener

elb.elb_listener(load_balancer_arn,target_group_arn)

print("""       ##########################################################
                #                                                        #           
                #        INFRASTRUCTURE SUCCESSFULLY PROVISIONED!        #
                #                                                        #
                ##########################################################      """)

