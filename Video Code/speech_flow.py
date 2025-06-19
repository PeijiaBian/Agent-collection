import requests
import time

# Generate API KEY, see: https://docs.speechflow.io/#/?id=generate-api-key
API_KEY_ID = "rvRlvuYwdEH6KJGA"
API_KEY_SECRET = "ODAhnZmLfR48je2k"
# The language code of the speech in media file.
# See more lang code: https://docs.speechflow.io/#/?id=ap-lang-list
LANG = "zh"
# The local path or remote path of media file.
FILE_PATH = "https://www.douyin.com/aweme/v1/play/?video_id=v0d00fg10000csln08vog65jheujrjag"

# The translation result type.
# 1, the default result type, the json format for sentences and words with begin time and end time.
# 2, the json format for the generated subtitles with begin time and end time.
# 3, the srt format for the generated subtitles with begin time and end time.
# 4, the plain text format for transcription results without begin time and end time.
RESULT_TYPE = 1

headers = {"keyId": API_KEY_ID, "keySecret": API_KEY_SECRET}


def create(file_path=None):
    create_data = {
        "lang": LANG,
    }
    files = {}
    create_url = "https://api.speechflow.io/asr/file/v1/create"
    
    # 如果传入了file_path参数，使用该参数
    if file_path:
        global FILE_PATH
        FILE_PATH = file_path
        
    if FILE_PATH.startswith('http'):
        create_data['remotePath'] = FILE_PATH
        print(f'submitting a remote file: {FILE_PATH}')
        response = requests.post(create_url, data=create_data, headers=headers)
    else:
        print(f'submitting a local file: {FILE_PATH}')
        create_url += "?lang=" + LANG
        files['file'] = open(FILE_PATH, "rb")
        response = requests.post(create_url, headers=headers, files=files)
    
    if response.status_code == 200:
        create_result = response.json()
        print(create_result)
        if create_result["code"] == 10000:
            task_id = create_result["taskId"]
        else:
            print("create error:")
            print(create_result["msg"])
            task_id = ""
    else:
        print('create request failed: ', response.status_code)
        task_id = ""
    return task_id


def query(task_id):
    query_url = "https://api.speechflow.io/asr/file/v1/query?taskId=" + task_id + "&resultType=" + str(RESULT_TYPE)
    print('querying transcription result')
    while (True):
        response = requests.get(query_url, headers=headers)
        if response.status_code == 200:
            query_result = response.json()
            if query_result["code"] == 11000:
                print('transcription result:')
                print(query_result)
                return query_result
            elif query_result["code"] == 11001:
                print('waiting')
                time.sleep(3)
                continue
            else:
                print(query_result)
                print("transcription error:")
                print(query_result['msg'])
                return query_result
        else:
            print('query request failed: ', response.status_code)
            return {
                "code": response.status_code,
                "msg": "query request failed"
            }

def main():
    task_id = create()
    if (task_id != ""):
        query(task_id)


# if __name__ == "__main__":
#     main()
