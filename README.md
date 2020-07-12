# SelfDrivingFleet-IOT
This project car devices to build and communicate in a fleet

Follow the below steps on the AWS console to run the demo project.

A. Create an IAM Policy


		1. In the AWS Management Console, click Services, and then click IAM to open the IAM dashboard.
		2. In the left navigation menu, click Policies.
		3. Click Create policy.
		4. Click the JSON tab.
		5. In the editor text box, replace the sample policy with the following:

		{
		  "Version": "2012-10-17",
		  "Statement": [
			{
			  "Effect": "Allow",
			  "Action": [
				"greengrass:*",
				"iot:*",
				"iotanalytics:*",
				"cloud9:*",
				"lambda:*",
				"s3:*",
				"sns:*",
				"iam:*",
				"cognito-identity:*",
				"cognito-sync:*",
				"cognito-idp:*",
				"logs:*",
				"ec2:*",
				"cloudwatch:*",
				"kms:ListAliases",
				"kms:DescribeKey",
				"cloudformation:DescribeStackResources",
				"tag:getResources"
			  ],
			  "Resource": "*"
			}
		  ]
		}
		6. Copy to clipboard
		7. Click Review Policy.
		8. For Name, enter scalableIoTPolicy.
		9. Click Create policy.
		
B. Create an IAM user and attach a policy to the user.

		1. In the AWS Management Console, click Services, and then click IAM to go to the IAM dashboard.
		2. In the left navigation menu, click Users.
		3. Click Add user.
		4. In the User name text box, enter scalableIoTUser.
		5. For Access type, select AWS Console access.
		6. For Console password, choose Custom password. Note the password.
		7. Remove the check mark next to User must create a new password at next sign-in.
		8. Click Next: Permissions.
		9. In the Set permissions section, click Attach existing policies directly.
		10. In the search text box for Filter, enter scalableIoTUser.
		11. Put a check mark next to scalableIoTPolicy in the filtered list.
		12. Click Next: Tags.
		13. Click Next: Review.
		14. Review the information, and click Create user. You should see a success message.
		15. Note the sign-in URL in the success message at the top. This is a special URL for IAM users, which includes your account ID.
		16. Click on the sign-in URL in the success message at the top. This will log you out.
		17. Sign in as the scalableIoTUser IAM user.

C. Create an AWS Cloud9 environment

		1. In the AWS Management Console, click Services, and then click Cloud9 to open the Cloud9 dashboard.
		2. Make sure you are in the Ireland.
		3. Click Create environment at the top-right corner.
		4. For Name, enter scalableOnAWS.
		5. Click Next step.
		6. On the Configure Settings page, leave the default settings, and click Next step.
		7. Review the details, and click Create environment. This should launch your AWS Cloud9 environment within a few minutes.
		
D. Setup your Cloud9 Environment, download the Car code and the AWS IoT CA Public Cert:

		1. Install the AWS IoT Device SDK Node package by running the following command in your AWS Cloud9 terminal.
			npm install aws-iot-device-sdk
		2. Use below command to create 10 folders for each car. 
		mkdir ~/environment/car1; mkdir ~/environment/car2; mkdir ~/environment/car3; mkdir ~/environment/car4; mkdir ~/environment/car5; mkdir ~/environment/car6; mkdir ~/environment/car7; mkdir ~/environment/car8; mkdir ~/environment/car9; mkdir ~/environment/car10;
		3. Copy the pub-sub.js file from git repo and copy in each car dir.
			cd ~/environment
			wget https://github.com/rohanbhutani1993/ScalableIoT---Project4/blob/master/pub-sub.js
			#Replace car number with <number> to copy file to each car folder.
			cp pub-sub.js car<number>/
			rm pub-sub.js
		4. Download the AWS IoT Certificate Authority Public Certificate
			cd ~/environment
			wget -O root-CA.crt https://www.amazontrust.com/repository/AmazonRootCA1.pem
E. Create Car IoT Thing, Certificate and Policy

		1. In your Cloud9 terminal, enter the following commands to create the car for all 10 cars.
			cd ~/environment/car<number>
			aws iot create-thing --thing-name car<number>
		2. To create the Certificate, enter the following command:
			aws iot create-keys-and-certificate --set-as-active --certificate-pem-outfile certificate.pem.crt --private-key-outfile private.pem.key
		3. To attach the Policy to the Certificate, enter the following command. Replace <certificateArn_changeme> with the value of the attribute certificateArn from the output of the previous command. 
			aws iot attach-policy --policy-name scalablePolicy --target <certificateArn_changeme>
		4. To attach the car2 Thing to the Certificate, enter the following command. Replace <certificateArn_changeme> with the value of the attribute certificateArn
		aws iot attach-thing-principal --thing-name car2 --principal <certificateArn_changeme>
		
F. Execute the code

		1. In the Cloud9 terminal, enter the following command to get your specific AWS IoT Endpoint.
			aws iot describe-endpoint --endpoint-type iot:Data-ATS > ~/environment/endpoint.json
		2. Execute the following commands to start the code for car1
			cd ~/environment/car1
			node pub-sub.js
		3. To listen to data in topic. In the AWS Management Console, click Services, and then click IoT Core to open the IoT Core console. Click Test in the left menu.
		4. In the Subscription topic, enter scalable/telemetry and click Subscribe to topic.
		
G. Create a Simple Notification Service Topic

		1. For the Topic name enter scalableSNSFuelTopic.
		2. Create subscription to start the process of subscribing your email address to the new SNS Topic you created.
H. Create an IAM Role

		1. In the AWS Management Console, click Services, and then click IAM to go to the IAM dashboard.
		2. In the left navigation menu, click Roles.
		3. Click Create role.
		4. Under Select type of trusted entity, AWS service should be selected.
		5. Under Choose the service that will use this role, select IoT.
		6. Under Select your use case, select IoT.
		7. Click Next: Permissions.
		8. Click Next: Tags.
		9.Click Next: Review.
		10. For Role name, enter scalableIoTRole.
		11. Click Create role.
		
I. Create an IoT Rule

		1. In the AWS Management Console, click Services, and then click IoT Core to go to the IoT console.
		2. In the left navigation menu, click Act. This is where you configure rules in IoT Core.
		3. Click Create a rule.
		4. For Name, enter scalableFuelRule.
		5. Under Set one or more actions, click Add action.
		6. Select Send a message as an SNS push notification.
		7. Click Configure action.
		8. Under SNS target, click Select.
		8. Next to scalableSNSFuelTopic, click Select.
		9. Under Message format, select RAW.
		10. Under Choose or create a role to grant AWS IoT access to perform this action, click Select.
		11. Next to scalableIoTRole, click Select.
		12. Click Add action.
			In the Rule query statement box, enter the following. You can paste this SQL statement:
		SELECT 
		  'The fuel level for ' + device + ' is currently at ' + round(fuel_level) + '%. The car is at ' + longitude + ' of longitude and ' + latitude + ' of latitude.' AS message
		FROM 'scalable/telemetry' 
		WHERE 
		  fuel_level < 25
		13. Click Create rule.
J. Run the code

		1. In the Cloud9 terminal, start car1 by executing the following commands.
			cd ~/environment/car1
			node pub-sub.js
			
K. Communicate between two cars:

		1. Install the AWS IoT Device SDK for Python
			sudo pip install AWSIoTPythonSDK
		2. Download the application code in project folder by running the following commands in your AWS Cloud9 terminal for all cars
		cd ~/environment/car<number>
		wget https://github.com/rohanbhutani1993/ScalableIoT---Project4/blob/master/communicate.py
		3. For each car folder change topic name at line:143 in communicate.py 
		 Ex: Change myAWSIoTMQTTClient.subscribe(dev1Topic, 1, onMessageCallback) to myAWSIoTMQTTClient.subscribe(dev2Topic, 1, onMessageCallback) for creating car2 communication file
		4. Start the code for each car in different terminals:
		cd ~/environment/car<number>
		python communicate.py
		5. Use command in command.txt file to test communication.
		Remember: '|'  seperates the message and the last part is the sender where you have to run command whereas the middle part is the car that receives the message.
		L.	Using SQS for communication between multiple instances	
		1.	In AWS Management console, click IAM. In IAM, click on users.
		2.	Select your username and click on Add Permissions in the permissions tab. Click on ‘Attach existing policies directly’. Search for SQS and select ‘AmazonSQSFullAccess’. 
		3.	Go to your Cloud 9 IDE and add create_queue.py, send_message_queue.py and receive.py files to each car folder. GO to car car1 folder with the following command – cd ~/environment/car1
		4.	 Run create_queue.py file with the following command – python2 create_queue.py. This command will create a stand queue which you can see in SQS console.
		5.	Run send_message_queue.py with the following command – python2 send_message_queue.py. This sends a message to the queue with 30 seconds delay.
		6.	Now on a second EC2 instance follow steps 1-3. 
		7.	Run receive.py file with the following command – python2 receive.py. You will be able to see the message printed at bottom of the terminal
		
		
M.  Lambda function and connecting to AWS IoT GreenGrass



	AWS Greengrass Documentation link

	<https://docs.aws.amazon.com/greengrass/latest/developerguide/setup-filter.ec2.html>

	1. Click AWS Management Console, click **Services**, and then click **IoT Greengrass** 
	2. Click **Create a Group**.
	3. Click **Use easy creation**. 
	4. In the **Group Name** 
	5. Click **Next**.
	6. In the **Name** field
	7. Click **Next**.
	8. Click **Create Group and Core**.
	9. **Download these resources as a tar.gz** 
	10. Click **Finish**.

	1. In the Cloud9 **terminal** enter the following commands:

   ```
   sudo adduser --system ggc_user
   sudo groupadd --system ggc_group
   ```

   ```
   echo 'fs.protected_hardlinks = 1' | sudo tee -a /etc/sysctl.d/00-defaults.conf
   echo 'fs.protected_symlinks = 1' | sudo tee -a /etc/sysctl.d/00-defaults.conf
   sudo sysctl --system
   ```

   ```
   cd /tmp
   curl https://raw.githubusercontent.com/tianon/cgroupfs-mount/951c38ee8d802330454bdede20d85ec1c0f8d312/cgroupfs-mount > cgroupfs-mount.sh
   chmod +x cgroupfs-mount.sh 
   sudo bash ./cgroupfs-mount.sh
   ```

	```
	cd /tmp
	wget https://d1onfpft10uf5o.cloudfront.net/greengrass-core/downloads/1.8.0/greengrass-linux-x86-64-1.8.0.tar.gz
	sudo tar -xzf greengrass-linux-x86-64-1.8.0.tar.gz -C /
	```

	1. Click on the folder **IoTOnAWS** in the directory tree on the left in Cloud9.

	2. Click **File > Upload Local Files...**.

	3. Click **Select files**.

	4. Select the **...-setup.tar.gz**.

	5. Click on the **x** icon to close the *Upload Files* window.

	6. In the Cloud9 **terminal** enter the following commands:

   ```
   cd /tmp
   mv ~/environment/*-setup.tar.gz setup.tar.gz
   sudo tar -xzf setup.tar.gz -C /greengrass
   ```

   ```
   cd /greengrass/certs/
   sudo wget -O root.ca.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem
   ```



	AWS Lambda Greengrass link

	<https://docs.aws.amazon.com/greengrass/latest/developerguide/create-lambda.html>

	Steps to create Lambda Function:

 

	1. In the AWS Management Console, click **Services** then click **Lambda** to go to the Lambda console.

	2. **Create a function**.

	3. For **Function** enter ScalableIotGreenGrass

	4. Select **Python 2.7**.

	5. Expand **Choose or create an execution role** under **Permissions**.

	6. In the **dropdown**, select **Create a new role from AWS policy templates**.

	7. For **Role name**, enter ScalableLambdaRole. 

	8. Click **Create function**.

	9. Click **Save** 

	10. Click **Actions > Publish new version**.

	11. Click **Publish**.

	###  

	### Lambda Part:

	1. Click **Lambdas**.

	2. Click **Add Lambda**.

	3. Click **Use existing Lambda**.

	4. Click the **radio button** next to **IoTGreengrassLambda**.

	5. Click **Next**.

	6. Click Version 1.

	7. Click **Finish**.

 

	Add the Subscription from car to Lambda for the topic:

	1. Click **Subscriptions**.

	2. Click **Add Subscription**.

	3. Under **Select a source**, click **Select**.

	4. Click **Devices**.

	5. Click **car1/car2/…**.

	6. Under **Select a target**, click **Select**.

	7. Click **Lambdas**.

	8. Click **IoTGreengrassLambda**.

	9. Click **Next**.

	10. For **Topic filter**, enter `scalable/telemetry`.

	11. Click **Next**.

	12. Click **Finish**.

 

	Add the Subscription from Lambda to AWS IoT for the *Greengrass* Topic:

	1. Click **Add Subscription**.

	2. Under **Select a source**, click **Select**.

	3. Click **Lambdas**.

	4. Click **IoTGreengrassLambda**.

	5. Under **Select a target**, click **Select**.

	6. Click **IoT Cloud**.

	7. Click **Next**.

	8. For **Topic filter**, enter `scalable/greengrass/telemetry`.

	9. Click **Next**.

	10. Click **Finish**.

	Deploy Greengrass Core:

	1. Click Actions > Deploy.

	2. Click Automatic detection.

	3. Click Deployments.

	4. Click Actions > Deploy.

	Commands in cloud9:

	`cd /greengrass/ggc/core`

	`sudo ./greengrassd start`

	`cd ~/enviorment/car1`

	`Node lambda.js` 		
