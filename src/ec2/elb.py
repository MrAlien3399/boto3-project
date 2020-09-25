import boto3
import time

class ELB:
    def __init__(self,client):
        self.client = boto3.client(client)
        """ :type : pyboto3.elbv2 """

    def load_balancer(self,elb_name,subnet01,subnet02,elb_sg):
        print('Creating Application  Load Balancer...')
        return self.client.create_load_balancer(
            Name = elb_name,
            Subnets = [
                subnet01,
                subnet02
            ],
            SecurityGroups = [
                elb_sg
            ],
            Type = 'application',

            IpAddressType = 'ipv4'
        )

    def target_group(self,tg_name,vpc_id):
        print("Waiting 59s For Instances to Keep Alive...")
        time.sleep(59)
        print('Creating Target Group...')
        return self.client.create_target_group(
            Name = tg_name,
            Protocol = 'HTTP',
            Port = 80,
            VpcId = vpc_id,
            HealthCheckProtocol = 'HTTP',
            HealthCheckPort = 'traffic-port',
            HealthCheckEnabled = True,
            HealthCheckPath='/',
            HealthCheckIntervalSeconds=35,
            HealthCheckTimeoutSeconds=5,
            HealthyThresholdCount=5,
            UnhealthyThresholdCount=2,
            Matcher= {
                'HttpCode' : '200'
            },
            TargetType = 'instance'
        )


    def register_targets(self,tg_arn,instance01_image_id,instance02_image_id):
        print('Registering Targets into Target Group...')
        return self.client.register_targets(
            TargetGroupArn = tg_arn,
            Targets = [
                {
                    'Id': instance01_image_id,
                    'Port': 80
                },
                {
                    'Id' : instance02_image_id,
                    'Port' : 80
                }
            ]
        )

    def elb_listener(self,lb_arn,tg_arn):
        print('Creating Listener...')
        return self.client.create_listener(
            LoadBalancerArn = lb_arn,
            Protocol = 'HTTP',
            Port = 80,
            DefaultActions = [
                {
                    'Type':'forward',
                    'TargetGroupArn' : tg_arn

                }
            ]
        )