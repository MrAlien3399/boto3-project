import time

class VPC:

    def __init__(self, client):
        self.client = client
        """ :type : pyboto3.ec2 """

    def create_vpc(self, cidrblock):
        print('Creating VPC with a CIDR Block of ' + cidrblock)
        return self.client.create_vpc(
            CidrBlock=cidrblock
        )

    def add_tag(self, resource_id, resource_name):
        print('Adding Tag ' + resource_name + 'to ' + resource_id)
        return self.client.create_tags(
            Resources=[resource_id],
            Tags=[{
                'Key': 'Name',
                'Value': resource_name
            }]
        )

    def create_igw(self):
        print('Creating an Internet Gateway...')
        return self.client.create_internet_gateway()

    def attach_igw(self, igw_id, vpc_id):
        print('Attaching an Internet Gateway ' + igw_id + 'to VPC ' + vpc_id)
        return self.client.attach_internet_gateway(
            InternetGatewayId=igw_id,
            VpcId=vpc_id
        )

    def create_subnet(self, vpc_id, az_id, cidr_block):
        print(
            'Creating Subnet in' + vpc_id + 'in the Availability Zone of ' + az_id + 'with the CIDR Block of ' + cidr_block)
        return self.client.create_subnet(
            VpcId=vpc_id,
            AvailabilityZoneId=az_id,
            CidrBlock=cidr_block
        )

    def create_route_table(self, vpc_id):
        print('Creating Route Table in VPC ' + vpc_id)
        return self.client.create_route_table(
            VpcId=vpc_id
        )

    def create_public_route(self, rtb_id, destination_cidr_block, igw_id):
        print('Creating Public Route to ' + igw_id)
        return self.client.create_route(
            RouteTableId=rtb_id,
            DestinationCidrBlock=destination_cidr_block,
            GatewayId=igw_id
        )

    def allow_auto_assing_ip_address_for_subnet(self,subnet_id):
        print('Activating Auto Assign Public Id on '+subnet_id)
        return self.client.modify_subnet_attribute(
            SubnetId = subnet_id,
            MapPublicIpOnLaunch = {'Value':True}
        )

    def allocate_elastic_ip(self):
        print('Allocating Elastic Ip Address...')
        return self.client.allocate_address(
            Domain='vpc'
        )

    def create_nat_gateway(self, allocation_id, subnet_id):
        print('Creating NAT Gateway in ' + subnet_id)
        NAT = self.client.create_nat_gateway(
            AllocationId=allocation_id,
            SubnetId=subnet_id
        )
        print('Wait For 30 seconds to complete creating NAT Gateway')
        time.sleep(30)
        return NAT

    def associate_subnet_with_route_table(self, subnet_id, rtb_id):
        print('Associating Subnet to the Route Table...')
        return self.client.associate_route_table(
            SubnetId=subnet_id,
            RouteTableId=rtb_id
        )

    def create_private_route_to_nat_igw(self, rtb_id, destination_cidr_block, nat_gw_id):
        print('Creating Private Route to NAT Gateway ' + nat_gw_id)
        return self.client.create_route(
            RouteTableId=rtb_id,
            DestinationCidrBlock=destination_cidr_block,
            NatGatewayId=nat_gw_id

        )

    def create_vpc_peering_conn(self, accepter_vpc_id, requester_vpc_id):
        print('Creating VPC Peering Connection...')
        print('Accepter VPC ID ' + accepter_vpc_id)
        print('Requester VPC ID ' + requester_vpc_id)
        return self.client.create_vpc_peering_connection(
            PeerOwnerId='108274497858',
            PeerVpcId=accepter_vpc_id,
            VpcId=requester_vpc_id,
            PeerRegion='ap-southeast-1'
        )

    def accept_vpc_peering_connection(self, vpc_peering_connection_id):
        print('Accepting VPC Peering Connection ' + vpc_peering_connection_id)
        return self.client.accept_vpc_peering_connection(
            VpcPeeringConnectionId=vpc_peering_connection_id
        )

    def create_route_to_peering_connection(self, rtb_id, destination_cidr_block, vpc_peering_conn_id):
        print('Created Route To VPC Peering Connection to ' + destination_cidr_block)
        return self.client.create_route(
            RouteTableId=rtb_id,
            DestinationCidrBlock=destination_cidr_block,
            VpcPeeringConnectionId=vpc_peering_conn_id
        )

