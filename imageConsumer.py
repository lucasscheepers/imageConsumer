import json
import boto3
import base64

def lambda_handler(event, context):
    print(event)

    s3 = boto3.resource('s3')
    sns = boto3.client('sns')

    for record in event['Records']:
        # Read the image message (extended message)
        print (f'{record} {type(record)}')
        body = record['body']
        print(f'{body} {type(body)}')
        extendedMessage = json.loads(body)
        print(f'{extendedMessage} {type(extendedMessage)}')

        bucketName = extendedMessage[1]['s3BucketName']
        itemName = extendedMessage[1]['s3Key']
        print(f'Extended message body at S3 {bucketName}:{itemName}')
        srcObj = s3.Object(bucketName, itemName)
        base64Img = srcObj.get()['Body'].read()
        decodedImageData = base64.decodebytes(base64Img)
        print(f'Retrieved and decoded the message body')

        # Save the image to the S3 bucket
        destBucketName = 'sqs-images-test'
        destItemName = 'files/' + itemName + '.jpg'
        destObj = s3.Object(destBucketName, destItemName)
        destObj.put(Body = decodedImageData, ACL = 'public-read')
        objectUrl = f'https://{destBucketName}.s3.amazonaws.com/{destItemName}';
        print(f'Image processed and stored at {objectUrl}')

        # Send notification to email subscribers
        sns.publish(TopicArn = 'arn:aws:sns:us-east-1:262887365742:fileEdited', Message = f'Photo processed and available for download. {objectUrl}')
        print(f'Notification sent to email subscribers')

        # Delete the S3 content of the extended message
        srcObj.delete()
        print(f'Extended message body deleted {bucketName}:{itemName}')

