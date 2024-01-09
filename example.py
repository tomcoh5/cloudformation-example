AWSTemplateFormatVersion: "2010-09-09"
Description: "Create an EC2 instance with Apache, a security group, and a load balancer with target group."

Parameters:
  KeyName:
    Type: String
    Description: "Name of an existing EC2 KeyPair to enable SSH access to the instance"

  SubnetId:
    Type: String
    Description: "ID of the first subnet where the EC2 instance should be launched"

  SubnetId2:
    Type: String
    Description: "ID of the second subnet where the EC2 instance should be launched"

  VpcId:
    Type: String
    Description: "ID of the VPC where the EC2 instance should be launched"

Resources:
  MySecurityGroup:
    Type: "AWS::EC2::SecurityGroup"
    Properties:
      GroupDescription: "Enable SSH and HTTP access"
      SecurityGroupIngress:
        - IpProtocol: "tcp"
          FromPort: 22
          ToPort: 22
          CidrIp: "0.0.0.0/0"
        - IpProtocol: "tcp"
          FromPort: 80
          ToPort: 80
          CidrIp: "0.0.0.0/0"

  MyEC2Instance:
    Type: "AWS::EC2::Instance"
    Properties:
      ImageId: "ami-079db87dc4c10ac91"
      InstanceType: "t2.micro"
      KeyName: !Ref KeyName
      SubnetId: !Ref SubnetId
      SecurityGroupIds:
        - !GetAtt MySecurityGroup.GroupId
      UserData:
        Fn::Base64: |
          #!/bin/bash
          yum update -y
          yum install -y httpd
          service httpd start
          chkconfig httpd on

  MyTargetGroup:
    Type: "AWS::ElasticLoadBalancingV2::TargetGroup"
    Properties:
      HealthCheckIntervalSeconds: 30
      HealthCheckPath: "/"
      HealthCheckPort: "80"
      HealthCheckProtocol: "HTTP"
      HealthCheckTimeoutSeconds: 5
      HealthyThresholdCount: 3
      Matcher:
        HttpCode: "200"
      Port: 80
      Protocol: "HTTP"
      TargetType: "instance"
      UnhealthyThresholdCount: 5
      VpcId: !Ref VpcId

  MyLoadBalancer:
    Type: "AWS::ElasticLoadBalancingV2::LoadBalancer"
    Properties:
      Subnets:
        - Ref: SubnetId
        - Ref: SubnetId2
      SecurityGroups:
        - !GetAtt MySecurityGroup.GroupId

  MyListener:
    Type: "AWS::ElasticLoadBalancingV2::Listener"
    Properties:
      DefaultActions:
        - Type: fixed-response
          FixedResponseConfig:
            StatusCode: 200
            ContentType: text/plain
            Content: "OK"
      LoadBalancerArn: !Ref MyLoadBalancer
      Port: 80
      Protocol: HTTP

  MyListenerRule:
    Type: "AWS::ElasticLoadBalancingV2::ListenerRule"
    Properties:
      Actions:
        - Type: "forward"
          TargetGroupArn: !Ref MyTargetGroup
      Conditions:
        - Field: "path-pattern"
          Values:
            - "/*"
      ListenerArn: !Ref MyListener

Outputs:
  WebsiteURL:
    Description: "URL of the website"
    Value: !GetAtt MyLoadBalancer.DNSName
