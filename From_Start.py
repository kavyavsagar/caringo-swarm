import shlex, subprocess
from os import getenv, listdir
from os.path import dirname, isfile, join
import urllib2
import csv
#import logging
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

DOCUMENTS_DIR="C:\Users\User4\Desktop\Caringo"
DOWNLOAD_CSV_DIR="C:\Users\User4\Desktop\Caringo\downloadcsv"
CARINGO_AUTH="admin:caringo"
CARINGO_AUTH_PASSWORD="caringo"
CARINGO_BUCKET_NAME="edcbucket"
CARINGO_DOMAIN_NAME="edcstorage"
CARINGO_HOST="http://192.168.0.121:8080/"

# ACCESS_KEY="f4bf06bdd3d2a0e43ae86f833350dea4"
# SECRET_KEY="kEUqM5KfJqEeyay9RcSlfJt4lGhSHb0C8Yxtg1EP"

param = "domain="+CARINGO_DOMAIN_NAME 
HOST_PATH = CARINGO_HOST+CARINGO_BUCKET_NAME+"/"

def main():
    print("Running..")
    res_files = upload_to_bucket()
    #print(res_files)
    print("List the responds of files")

def get_all_files():
	onlyfiles = [f for f in listdir(DOCUMENTS_DIR) if isfile(join(DOCUMENTS_DIR, f)) and f.endswith('.pdf')] 
	print("getting files.")
	return onlyfiles

def upload_to_bucket():
	ls_files = get_all_files()
	up_res = []
	
	print("upload files.")
	for file in ls_files:		
		if(is_file_exists(file)):
			cmd = 'curl -v -u '+CARINGO_AUTH+' -X PUT -H Content-type:application/pdf --data-binary @'+ join(DOCUMENTS_DIR, file) +' '+ HOST_PATH + file +'?'+param
		else:
			cmd = 'curl -v -u '+CARINGO_AUTH+' -X POST -H Content-type:application/pdf --data-binary @'+ join(DOCUMENTS_DIR, file) +' '+ HOST_PATH + file +'?'+param	   	
		proc = subprocess.call(cmd, shell=True)  
		presigned = create_presigned_url(CARINGO_BUCKET_NAME, file)	   
		up_res.append(presigned)

	return up_res

def is_file_exists(item):
	command = 'curl -v -I --post301 --location-trusted ' + HOST_PATH + item +'?'+param
	proc = subprocess.Popen(command, stdout=subprocess.PIPE)
	(out, err) = proc.communicate()

	print("GET INFO")	
	if "404 Not Found" in out:
		return 0 
	else:
		return 1
        
def export_csv():
	print("Export files to csv.")
	with open(DOWNLOAD_CSV_DIR, 'wb') as csvfile:
	    filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	    filewriter.writerow(['Filename', 'Filepath'])
	    for x in onlyfiles: filewriter.writerow([x, HOST_PATH + x +'?'+param])

def create_presigned_url(bucket_name, object_name, expiration=3600):
    # Generate a presigned URL for the S3 object   
    #
	s3_client = boto3.client('s3', 	
		region_name=CARINGO_DOMAIN_NAME, 	
		aws_access_key_id=ACCESS_KEY,
		aws_secret_access_key=SECRET_KEY,
		config=Config(signature_version='s3v4', s3={'addressing_style': 'path'}))

	Params   = {'Bucket': bucket_name, 'Key': object_name}
	response = s3_client.generate_presigned_url('get_object', Params, expiration)
	print("Signed URL")
	print(response)
	# The response contains the presigned URL
	return response 

if __name__ == '__main__':
    main()       
