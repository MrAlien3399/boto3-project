
class EC2:
    def __init__(self,client):
        self.client = client

    def create_key_pair(self,key_pair_name):
        print('Creating Key Pair Named '+key_pair_name)
        with open (key_pair_name+'.pem','w') as outfile:
            key_pair = self.client.create_key_pair(
                KeyName = key_pair_name
            )
            key_pair_out = key_pair['KeyMaterial']
            outfile.write(key_pair_out)


    def create_security_group(self,group_name,description,vpc_id):
        print('Creating Security Group with a name '+group_name)
        return self.client.create_security_group(
            GroupName = group_name,
            Description = description,
            VpcId = vpc_id
        )

    def add_rule_to_security_group(self,security_group_id,cidr_ip):
        print('Adding Rules to Security Group of '+security_group_id)
        return self.client.authorize_security_group_ingress(
            GroupId = security_group_id,
            IpPermissions = [{
                'IpProtocol' : 'tcp',
                'FromPort' : 22,
                'ToPort' : 22,
                'IpRanges' : [{'CidrIp':cidr_ip}]
            },
            {
                'IpProtocol' : 'tcp',
                'FromPort' : 80,
                'ToPort' : 80,
                'IpRanges' : [{'CidrIp':cidr_ip}]
            }
            ]
        )

    def launch_ec2_instance(self,image_id,key_name,min_count,max_count,instance_type,security_group_id,subnet_id,user_data):
        print('Launching EC2 Instance type of '+instance_type+'in Subnet '+subnet_id)
        return self.client.run_instances(
            ImageId = image_id,
            KeyName = key_name,
            MinCount = min_count,
            MaxCount = max_count,
            InstanceType = instance_type,
            SecurityGroupIds = [security_group_id],
            SubnetId = subnet_id,
            UserData = user_data
        )