import os

import boto3


class BotoFramework:

    def getTempUrl(self, questions, duration):
        s3 = boto3.client('s3', aws_access_key_id=os.environ['access_key'], aws_secret_access_key=os.environ['secret_key'])
        list_questions = []
        bucket_name = []
        key_name = []
        list_url = []
        for i in questions:
            list_questions.append(i[0])

        for j in range(0, len(list_questions)):
            bucket_name.append(list_questions[j].split("/", 1)[0])
            key_name.append((list_questions[j].strip(list_questions[j].split("/", 1)[0])).replace("/", "", 1))
            params = {
                'Bucket': bucket_name[j],
                'Key': key_name[j]
            }
            url = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=duration)
            list_url.append(url)

        return list_url
